# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from bs4 import BeautifulSoup
from cds2md.cache import cache_key
from cds2md.defs import CACHE_DB
from cds2md.logger import logger
from cds2md.translator import Translator
from cds2md.translator import TranslatorContext
from dataclasses import dataclass
from pathlib import Path
from slugify import slugify
import json
import shutil


@dataclass
class AttachmentCache:
    id: int
    name: str
    version: int
    target_path: Path | None = None


@dataclass
class PageCache:
    attachments: list[AttachmentCache]
    body: str
    id: int
    title: str
    version: int
    parent_id: int | None = None
    target_path: Path | None = None


def convert(opts: Namespace) -> bool:
    # ensure cache directory is prepared
    cache_dir = opts.cache / cache_key(opts)
    cache_db = cache_dir / CACHE_DB
    if not cache_db.is_file():
        logger.error('no cache database found')
        return False

    # extract cached fetch data to be processed
    pages_cache = []
    pageid2cache = {}

    with cache_db.open() as f:
        pages = json.load(f)['pages']

        for page_id_str, page_data in pages.items():
            page_atachments = page_data['attachments']
            page_id = int(page_id_str)
            page_parent = page_data['parent']
            page_version = page_data['version']
            page_cache_dir = cache_dir / page_id_str
            page_cache_filename = f'{page_id}-{page_version}.json'
            page_cache_file = page_cache_dir / page_cache_filename

            attachments = []
            for attachment_name, attachment_data in page_atachments.items():
                attachment_id = attachment_data['id']
                attachment_version = attachment_data['version']

                attachment_cache = AttachmentCache(
                    id=attachment_id,
                    name=attachment_name,
                    version=attachment_version,
                )
                attachments.append(attachment_cache)

            with page_cache_file.open() as f2:
                page_cache_data = json.load(f2)
                page_body = page_cache_data['body']
                page_title = page_cache_data['title']

                page_cache = PageCache(
                    attachments=attachments,
                    body=page_body,
                    id=page_id,
                    parent_id=page_parent,
                    title=page_title,
                    version=page_version,
                )
                pageid2cache[page_id] = page_cache
                pages_cache.append(page_cache)

    # determine the paths for each page cache to be stored
    attachment2target: dict[tuple[str, str], str] = {}
    title2target: dict[str, str] = {}
    reserved_attachment_targets = set()

    for page_cache in pages_cache:
        title_slug = slugify(page_cache.title)
        md_filename = f'{title_slug}.md'

        # if a flat setup, place the page at the root of the output
        if opts.flat:
            page_path = opts.output / md_filename
        # if using hierarchy hints, determine based with parent data
        else:
            path_parts = [
                md_filename,
            ]

            target_parent = page_cache.parent_id
            while target_parent:
                parent = pageid2cache.get(target_parent)
                assert parent
                parent_slug = slugify(parent.title)
                path_parts.append(parent_slug)
                target_parent = parent.parent_id

            page_path = opts.output
            for s in reversed(path_parts):
                page_path = page_path / s

        page_cache.target_path = page_path

        root_path = page_path.relative_to(opts.output)
        page_full_slug = root_path.as_posix()
        title2target[page_cache.title] = page_full_slug

        for attachment_cache in page_cache.attachments:
            attachment_pathname = Path(attachment_cache.name)
            attachment_name = slugify(attachment_pathname.stem)
            attachment_ext = slugify(attachment_pathname.suffix)

            attachment_suffix = 1
            while True:
                sfx = attachment_suffix if attachment_suffix > 1 else ''
                attachment_filename = f'{attachment_name}{sfx}.{attachment_ext}'
                attachment_path = page_path.parent / attachment_filename

                # check if we have a conflicting attachment
                if attachment_path in reserved_attachment_targets:
                    attachment_suffix += 1
                    continue

                break

            attachment_cache.target_path = attachment_path
            reserved_attachment_targets.add(attachment_path)

            attachment_ref = (page_full_slug, attachment_cache.name)

            attachment_root_path = attachment_path.relative_to(opts.output)
            attachment_full_slug = attachment_root_path.as_posix()
            attachment2target[attachment_ref] = attachment_full_slug

    # process each page
    ctx = TranslatorContext(
        attachment2target=attachment2target,
        opts=opts,
        title2target=title2target,
    )

    for page_cache in pages_cache:
        assert page_cache.target_path
        doc_path = page_cache.target_path.as_posix()

        # parse the page's body
        logger.debug(f'processing body of page: {doc_path}')
        soup = BeautifulSoup(page_cache.body, 'html.parser')

        # translate the parsed content into a markdown output
        translator = Translator(ctx, page_cache.title)
        logger.debug(f'walking page: {doc_path}')
        translator.walk(soup)

        # build the final markdown document contents
        final_body = ''.join(translator.output).strip() + '\n'

        # write the markdown content to its output file
        assert page_cache.target_path
        md_file = page_cache.target_path
        md_file.parent.mkdir(parents=True, exist_ok=True)
        logger.debug(f'writing to markdown file: {md_file.as_posix()}')

        if md_file.is_dir():
            logger.error('cannot write markdown into path '
                        f'that is a directory: {md_file.as_posix()}')
            return False

        md_file.write_text(final_body)

        # process each attachment
        if page_cache.attachments:
            logger.debug(f'processing attachments for page: {doc_path}')
            page_id = page_cache.id
            attachment_cache_dir = cache_dir / f'{page_id}' / 'attachments'

            for attachment_cache in page_cache.attachments:
                attachment_id = attachment_cache.id
                attachment_version = attachment_cache.version
                attachment_fname = f'{attachment_id}-{attachment_version}.dat'
                attachment_data = attachment_cache_dir / attachment_fname

                assert attachment_cache.target_path
                attachment_folder = attachment_cache.target_path.parent
                attachment_folder.mkdir(parents=True, exist_ok=True)

                attachment_desc = attachment_cache.target_path.as_posix()
                logger.debug(f'copying attachment (source): {attachment_data}')
                logger.debug(f'copying attachment (target): {attachment_desc}')
                shutil.copy2(attachment_data, attachment_cache.target_path)

    return True

