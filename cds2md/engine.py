# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from cds2md import __version__ as cds2md_version
from cds2md.defs import Action
from cds2md.convert import convert
from cds2md.fetch import fetch
from cds2md.logger import logger
from cds2md.validate_connection import validate_connection
from cds2md.validate_space import validate_space
import httpx
import ssl


def engine(opts: Namespace) -> None:
    # perform any action requiring remote work
    if opts.action in [Action.ALL, Action.CONNECTION_CHECK, Action.FETCH]:
        perform_web_action(opts)

    # perform process action
    if opts.action in [Action.ALL, Action.PROCESS]:
        process(opts)


def perform_web_action(opts: Namespace) -> None:
    # prepare an http client for requests
    timeout = httpx.Timeout(
        connect=opts.timeout,
        read=15.0,
        write=5.0,
        pool=5.0,
    )

    headers: dict[str, str] = {}
    headers |= opts.headers
    headers |= {
        # will only process json
        'Accept': 'application/json',
        # configure confluence pat to perform queries with
        'Authorization': f'Bearer {opts.confluence_token}',
        # user agent for our interactions
        'User-Agent': f'Cds2md/{cds2md_version}',
        # ignore csrf
        'X-Atlassian-Token': 'no-check',
    }

    # setup ssl context
    ssl_context = ssl.create_default_context()
    if opts.ca_certificate:
        ssl_context.load_verify_locations(cafile=opts.ca_certificate)
    elif opts.ignore_tls:
        ssl_context = False  # type: ignore[assignment]

    with httpx.Client(
                headers=headers,
                timeout=timeout,
                verify=ssl_context,
            ) as client:

        # perform connection check action
        if opts.action in [Action.ALL, Action.CONNECTION_CHECK]:
            connection_check(opts, client)

        # perform data fetch action
        if opts.action in [Action.ALL, Action.FETCH]:
            fetch_attempt(opts, client)


def connection_check(opts: Namespace, client: httpx.Client) -> None:
    logger.info('validating availability of confluence instance...')
    logger.debug(f'instance: {opts.confluence_url}')

    if not validate_connection(opts, client):
        raise SystemExit(3)

    logger.info('confluence instance appears to be online')


def fetch_attempt(opts: Namespace, client: httpx.Client) -> None:
    logger.info('validating the confluence space can be found...')
    logger.debug(f'space-key: {opts.confluence_space_key}')

    # verify the space exists
    if not validate_space(opts, client):
        raise SystemExit(4)

    logger.info('confluence space has been detected')

    # try to pull space content
    logger.info('attempting to fetch content...')

    if not fetch(opts, client):
        raise SystemExit(5)


def process(opts: Namespace) -> None:
    logger.info('converting cached data into markdown files')

    if not convert(opts):
        raise SystemExit(3)

    logger.info('conversion completed')
