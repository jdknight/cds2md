# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from dataclasses import dataclass
from hashlib import sha1


@dataclass
class AttachmentMetaCache:
    id: int
    page_id: int
    size: int
    title: str
    type: str
    url: str
    version: int


@dataclass
class PageMetaCache:
    id: int
    version: int
    parent_id: int | None = None


def cache_key(opts: Namespace) -> str:
    """
    generate a cache string

    Build a cache string based on the configured runtime options. This will
    be used to populate a cache path based on the Confluence URL and space.

    Args:
        opts: the runtime options

    Returns:
        the cache string
    """
    value = f'{opts.confluence_url}--{opts.confluence_space_key}'
    return sha1(value.encode()).hexdigest()  # noqa: S324
