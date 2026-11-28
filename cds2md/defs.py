# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from enum import StrEnum


# name of the cache database for a cached dataset
CACHE_DB = 'cache.json'

# name of the cache directory
CACHE_DIRNAME = '.cds2md-cache'

# name of the configuration file
CFG_NAME = 'conf.py'


class Action(StrEnum):
    ALL = 'all'
    CONNECTION_CHECK = 'connection-check'
    FETCH = 'fetch'
    PROCESS = 'process'


class AdmonitionType(StrEnum):
    DEFAULT = 'default'
    DOCUSAURUS = 'docusaurus'
    GITHUB = 'github'
    GITLAB = 'gitlab'
    MYST  = 'myst'
    PLAIN = 'plain'


class AnchorType(StrEnum):
    DEFAULT = 'default'
    HTML = 'html'
    MYST  = 'myst'
