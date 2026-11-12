# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from cds2md import __version__ as cds2md_version
from cds2md.cache import AttachmentMetaCache
from cds2md.cache import PageMetaCache
from cds2md.cache import cache_key
from cds2md.defs import CACHE_DB
from cds2md.logger import logger
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from email.utils import mktime_tz
from email.utils import parsedate_tz
from functools import wraps
from pathlib import Path
from typing import Any
from typing import Concatenate
from typing import ParamSpec
from typing import TypeAlias
from typing import TypeVar
from urllib.parse import parse_qsl
from urllib.parse import urlparse
import httpx
import json
import math
import random
import time


# number of elements to fetch for bulk requests
# (Confluence v2 APIs indicate a max of 250; a good enough number as any)
BULK_LIMIT = 250

# maximum limit (in seconds) to automatically stop querying
MAX_RATE_LIMIT = 120

# the maximum times a request will be retried until stopping (rate limiting)
RATE_LIMITED_MAX_RETRIES = 5

# the maximum duration (in seconds) a retry on a rate-limited request can be
# delayed
RATE_LIMITED_MAX_RETRY_DURATION = 30

# the maximum times a request will be retried until stopping (erred instance)
REMOTE_ERR_MAX_RETRIES = 2

# the maximum duration (in seconds) a retry on a erred request can be delayed
REMOTE_ERR_MAX_RETRY_DURATION = 4

# errors to auto-retry publishing on; see:
# https://everything.curl.dev/usingcurl/downloads/retry.html#retry
TRANSIENT_ERRORS = (
    408,
    500,
    502,
    503,
    504,
)


@dataclass
class FetchState:
    http_client: httpx.Client
    opts: Namespace
    rate_limit_last: float = 1
    rate_limit_next: int | None = None


P = ParamSpec('P')
R = TypeVar('R')
AsyncFunc: TypeAlias = Callable[P, R]
AsyncFuncWithState = Callable[Concatenate[FetchState, P], R]


def fetch(opts: Namespace, client: httpx.Client) -> int:
    """
    request to publish a manifest to a confluence instance

    This call accepts a manifest and attempts to publish this information to
    the configured Confluence instance. It will cycle through the data,
    determine pages to publish, publish these pages; followed by cycling
    through any attachments to publish.

    Args:
        opts: the program options
        client: the web client to query/fetch from confluence

    Returns:
        how many pages where prepared
    """

    state = FetchState(
        http_client=client,
        opts=opts,
    )

    # query the space for all known page identifiers
    pages = fetch_space_pages(state)

    # fetch all detected pages
    page_count = 1
    total_pages = len(pages)

    # ensure cache directory is prepared
    cache_dir = opts.cache / cache_key(opts)
    try:
        cache_dir.mkdir(parents=True)

        # provide a little helpful metadata hint for users inspecting the
        # cache content and want to see what the key maps to
        cache_dir_hint = cache_dir / 'metadata.txt'
        logger.debug(f'writing cache metadata hint: {cache_dir_hint}')
        cache_dir_hint.write_text(f'''\
confluence-url: {opts.confluence_url}
confluence-space-key: {opts.confluence_space_key}
''')
    except FileExistsError:
        pass

    # about to process a newly entire cache state -- clear the previous
    # data before we write content until we have acquired all new data
    cache_db = cache_dir / CACHE_DB
    cache_db.unlink(missing_ok=True)

    cache_db_state: dict[str, Any] = {
        'cds2md-version': cds2md_version,
        'pages': {},
    }

    # for each found page, fetch its contents into the cache
    for page in pages:
        # ensure a page's cache directory exists
        page_cache_dir = cache_dir / str(page.id)
        page_cache_dir.mkdir(exist_ok=True)

        # check if we have already cached this page's version
        page_cache_filename = f'{page.id}-{page.version}.json'
        page_cache_file = page_cache_dir / page_cache_filename

        # skip if we have already cached this page
        status = ''
        if page_cache_file.exists():
            status = ' (cache)'
        else:
            # query information about the page
            page_title, page_body = fetch_page(state, page)

            with page_cache_file.open('w') as f:
                json.dump({
                    'body': page_body,
                    'cds2md-timestamp': datetime.now(UTC).isoformat(),
                    'cds2md-version': cds2md_version,
                    'title': page_title,
                }, f, indent=4)
                f.write('\n')

        logger.info(
            f'[fetch] page ({page_count}/{total_pages}): {page.id}{status}')
        page_count += 1

        cache_db_state['pages'][page.id] = {
            'attachments': {},
            'parent': page.parent_id,
            'version': page.version,
        }

    # also check for attachments for each page
    attachments = []
    for page in pages:
        page_attachments = fetch_attachments(state, page)
        attachments.extend(page_attachments)

    # fetch all detected attachments
    attachment_count = 1
    total_attachments = len(attachments)

    for attachment in attachments:
        # ensure a attachment's cache directory exists
        page_id = attachment.page_id
        attachment_cache_dir = cache_dir / str(page_id) / 'attachments'
        attachment_cache_dir.mkdir(exist_ok=True)

        # check if we have already cached this attachment's version
        name = f'{attachment.id}-{attachment.version}'
        attachment_cache_filename = f'{name}.dat'
        attachment_cache_metadata = f'{name}.json'
        attachment_file = attachment_cache_dir / attachment_cache_filename
        attachment_meta = attachment_cache_dir / attachment_cache_metadata

        # skip if we have already cached this attachment
        status = ''
        if attachment_meta.exists():
            status = ' (cache)'
        else:
            # query information about the attachment
            fetch_attachment(state, attachment, attachment_file)

            with attachment_meta.open('w') as f:
                json.dump({
                    'cds2md-timestamp': datetime.now(UTC).isoformat(),
                    'cds2md-version': cds2md_version,
                    'size': attachment.size,
                    'title': attachment.title,
                    'type': attachment.type,
                }, f, indent=4)
                f.write('\n')

        logger.info('[fetch] attachment '
            f'({attachment_count}/{total_attachments}): '
            f'{attachment.id}{status}')
        attachment_count += 1

        cache_db_state['pages'][page_id]['attachments'][attachment.title] = {
            'id': attachment.id,
            'version': attachment.version,
        }

    # fetch process complete -- write to new database state
    with cache_db.open('w') as f:
        json.dump(cache_db_state, f, indent=4)
        f.write('\n')

    return page_count


def confluence_error_retries() -> Callable[[AsyncFunc], AsyncFunc]:
    """
    a confluence error retry "decorator"

    A utility "decorator" to handle automatic attempt to retry an API call
    if Confluence reports an unexpected server error (e.g. a 5xx error).
    There can be issues where Confluence may have issues with a transaction
    on a page update, or an unexpected error processing properties on a page.
    If such a call is detected, the call will be retried again in hopes that
    it was a one time occurrence.
    """
    def _decorator(func: AsyncFunc[P, R]) -> AsyncFunc[P, R]:
        @wraps(func)
        def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except httpx.HTTPStatusError as exc:
                    # if max attempts have been reached, stop any more attempts
                    if attempt > REMOTE_ERR_MAX_RETRIES:
                        raise

                    # retry on transient errors
                    if exc.response.status_code not in TRANSIENT_ERRORS:
                        raise

                    # configure the delay
                    delay = float(REMOTE_ERR_MAX_RETRY_DURATION)

                    # add jitter
                    delay += random.uniform(0.0, 0.5)  # noqa: S311

                    # wait the calculated delay before retrying again
                    reported_delay = math.ceil(delay)
                    logger.info('unexpected rest response detected; '
                                f'retrying in {reported_delay} seconds...')
                    time.sleep(delay)
                    attempt += 1

        return _wrapper
    return _decorator


def rate_limited_retries() -> Callable[[AsyncFuncWithState], AsyncFuncWithState]:
    """
    a rest rate limited "decorator"

    A utility "decorator" to handle rate-limited retries if Confluence reports
    that API calls should be limited.
    """
    def _decorator(func: AsyncFuncWithState[P, R]) -> AsyncFuncWithState[P, R]:
        @wraps(func)
        def _wrapper(state: FetchState, *args: P.args, **kwargs: P.kwargs) -> R:
            # if confluence asked us to wait so many seconds before a next
            # api request, wait a moment
            if state.rate_limit_next:
                delay = float(state.rate_limit_next)
                logger.debug('rate-limit header detected; '
                            f'waiting {math.ceil(delay)} seconds...')
                time.sleep(delay)
                state.rate_limit_next = None

            # if we have imposed some rate-limiting requests where confluence
            # did not provide retry information, slowly decrease our tracked
            # delay if requests are going through
            state.rate_limit_last = max(state.rate_limit_last / 2, 1)

            attempt = 1
            while True:
                try:
                    return func(state, *args, **kwargs)
                except httpx.HTTPStatusError as exc:
                    # ignore non-rate limited
                    code = exc.response.status_code
                    if code != httpx.codes.TOO_MANY_REQUESTS:
                        raise

                    # if max attempts have been reached, stop any more attempts
                    if attempt > RATE_LIMITED_MAX_RETRIES:
                        raise

                    # if confluence or a proxy reports a retry-after delay
                    # (to pace us), track it to delay the next request made
                    # (https://datatracker.ietf.org/doc/html/rfc2616.html#section-14.37)
                    raw_delay = exc.response.headers.get('Retry-After')
                    if raw_delay:
                        new_delay = 0
                        try:
                            # attempt to parse a seconds value from the header
                            new_delay = int(raw_delay)
                        except ValueError:
                            # if seconds are not provided, attempt to parse
                            parsed_dtz = parsedate_tz(raw_delay)
                            if parsed_dtz:
                                target_datetime = mktime_tz(parsed_dtz)
                                new_delay = int(target_datetime - time.time())

                        if new_delay > 0:
                            state.rate_limit_next = new_delay

                            # if this is a long rate-limit, do not even try
                            # to interact; either rate limiting is disabled
                            # or administration/proxy is having issues or is
                            # too strict in quota
                            if new_delay >= MAX_RATE_LIMIT:
                                logger.warning(
                                    'long rate-limit duration; will stop')
                                state.rate_limit_next = None
                                raise

                    # determine the amount of delay to wait again -- either
                    # from the provided delay (if any) or exponential back-off
                    if state.rate_limit_next:
                        delay = float(state.rate_limit_next)
                        state.rate_limit_next = None
                    else:
                        delay = 2 * state.rate_limit_last

                    # cap delay to a maximum
                    delay = min(delay, RATE_LIMITED_MAX_RETRY_DURATION)

                    # add jitter
                    delay += random.uniform(0.3, 1.3)  # noqa: S311

                    # wait the calculated delay before retrying again
                    logger.debug('rate-limit response detected; '
                                f'waiting {math.ceil(delay)} seconds...')
                    time.sleep(delay)
                    state.rate_limit_last = delay
                    attempt += 1

        return _wrapper
    return _decorator


@confluence_error_retries()
@rate_limited_retries()
def fetch_attachment(state: FetchState,
        attachment: AttachmentMetaCache, target: Path) -> None:
    """
    fetch attachment data from the confluence instance

    This call is used to fetch attachment data from a Confluence instance.

    Args:
        state: the fetch state
        attachment: the attachment metadata
        target: path to populate attachment data
    """

    # invoke a url download
    logger.debug(f'about to download attachment: {attachment.url}')

    with state.http_client.stream(
                'GET',
                attachment.url,
                headers={
                    'Accept': '*/*',
                },
            ) as rsp:
        rsp.raise_for_status()

        with target.open('wb') as f:
            for chunk in rsp.iter_bytes(chunk_size=8192):
                f.write(chunk)

    logger.debug(f'downloaded attachment ({attachment.id}): zzzz')


@confluence_error_retries()
@rate_limited_retries()
def fetch_attachments(state: FetchState,
        page: PageMetaCache) -> list[AttachmentMetaCache]:
    """
    fetch page data from the confluence instance

    This call is used to fetch page data from a Confluence instance, if the
    page exists.

    Args:
        state: the fetch state
        page: the page cache

    Returns:
        set of found page identifiers
    """

    attachments: list[AttachmentMetaCache] = []
    search_fields = {
        'limit': f'{BULK_LIMIT}',
        'expand': 'version',
    }

    # query for this page's attachments
    logger.debug(f'about to query attachments for page identifier: {page.id}')
    fetch_api = f'{state.opts.confluence_url}/content/{page.id}/child/attachment'
    rsp = state.http_client.get(fetch_api, params=search_fields)

    rsp.raise_for_status()
    data = rsp.json()

    idx = 0
    while data.get('results'):
        for result in data['results']:
            attachment_id = int(result['id'])
            attachment_size = result['extensions']['fileSize']
            attachment_title = result['title']
            attachment_type = result['extensions']['mediaType']
            attachment_version = result.get('version', {}).get('number', 1)

            base_url = data['_links']['base']
            download_part = result['_links']['download']
            attachment_url = f'{base_url}{download_part}'

            attachment_entry = AttachmentMetaCache(
                id=attachment_id,
                page_id=page.id,
                size=attachment_size,
                title=attachment_title,
                type=attachment_type,
                url=attachment_url,
                version=attachment_version,
            )

            attachments.append(attachment_entry)

        count = len(data['results'])
        if count != BULK_LIMIT:
            break

        idx += count
        next_fields = _next_page_fields(data, search_fields, idx)
        if not next_fields:
            break

        rsp = state.http_client.get(fetch_api, params=next_fields)
        rsp.raise_for_status()
        data = rsp.json()

    return attachments


@confluence_error_retries()
@rate_limited_retries()
def fetch_space_pages(state: FetchState) -> list[PageMetaCache]:
    """
    fetch all page identifiers that exist in the configure space

    This call is used to fetch a set of all pages that are hosted in a
    configured Confluence space.

    Args:
        state: the fetch state

    Returns:
        list of all detected page metadata information for a space
    """

    pages: list[PageMetaCache] = []

    search_fields = {
        'cql': f'space={state.opts.confluence_space_key}+and+type=page',
        'expand': 'ancestors,version',
        'limit': f'{BULK_LIMIT}',
    }

    # query for this page's descendants
    fetch_api = f'{state.opts.confluence_url}/content/search'
    rsp = state.http_client.get(fetch_api, params=search_fields)

    rsp.raise_for_status()
    data = rsp.json()

    idx = 0
    while data.get('results'):
        for result in data['results']:
            page_id = int(result['id'])
            page_version = result.get('version', {}).get('number', 1)

            parent_id = None
            ancestor_entries = result.get('ancestors')
            if ancestor_entries:
                parent_id = int(result['ancestors'][-1]['id'])

            page_entry = PageMetaCache(
                id=page_id,
                version=page_version,
                parent_id=parent_id,
            )

            pages.append(page_entry)

        count = len(data['results'])
        if count != BULK_LIMIT:
            break

        idx += count
        next_fields = _next_page_fields(data, search_fields, idx)
        if not next_fields:
            break

        rsp = state.http_client.get(fetch_api, params=next_fields)
        rsp.raise_for_status()
        data = rsp.json()

    return pages


def _next_page_fields(rsp: dict, fields: dict, offset: int) -> dict | None:
    """
    extract next query fields from a response

    For paged search requests, Confluence can report a "next" link to use
    for the "next page". This call can be used to extract the query options
    provided by Confluence that should be included in a next request.

    Original CQL search calls would use a "start" offset to manage pages.
    Note on Confluence Data Center, the "start" offset may still be used.

    Args:
        rsp: the response to pull a next query from
        fields: the recommended search fields
        offset: the recommended start offset

    Returns:
        the extract query fields
    """

    reported_links = rsp.get('_links')
    if reported_links:
        next_query = reported_links.get('next')
        if next_query:
            try:
                parsed = urlparse(next_query)
                return dict(parse_qsl(parsed.query))
            except ValueError:
                return None

            return None

    total_sz = rsp.get('totalSize')
    if total_sz and total_sz > offset:
        sub_search_fields = dict(fields)
        sub_search_fields['start'] = offset
        return sub_search_fields

    return None


@confluence_error_retries()
@rate_limited_retries()
def fetch_page(state: FetchState, page: PageMetaCache) -> tuple[str, str]:
    """
    fetch page data from the confluence instance

    This call is used to fetch page data from a Confluence instance, if the
    page exists.

    Args:
        state: the fetch state
        page: the page to fetch

    Returns:
        tuple of the page's title and body
    """

    # query if this page already exists
    logger.debug(f'about to fetch page identifier: {page.id}')

    fetch_api = f'{state.opts.confluence_url}/content/{page.id}'
    rsp = state.http_client.get(fetch_api, params={
        'expand': 'body.storage',
        'version': page.version,
    })

    rsp.raise_for_status()
    data = rsp.json()

    page_body = data['body']['storage']['value']
    page_title = data['title']

    logger.debug(f'fetched page ({page.id}; v{page.version}): {page_title}')

    return page_title, page_body
