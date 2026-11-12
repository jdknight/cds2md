# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import ArgumentParser
from argparse import ArgumentTypeError
from argparse import Namespace
from argparse import RawDescriptionHelpFormatter
from cds2md import __version__ as cds2md_version
from cds2md.defs import Action
from cds2md.defs import AdmonitionType
from cds2md.defs import CACHE_DIRNAME
from cds2md.logger import logger
from cds2md.logger import logger_handler
from collections.abc import Sequence
from pathlib import Path
from urllib.parse import urlparse
import logging
import os
import sys


# time (in seconds) for all rest connection requests
DEFAULT_CONNECTION_TIMEOUT = 5.0

# attempt to wrap text to the following character count
DEFAULT_WRAP = 80


def process_options(args: Sequence[str] | None = None) -> Namespace:
    """
    process program options

    This call will process program options for a given run. This will look at
    both command line options and environment configurations to ready for a
    query event.

    Args:
        args (optional): custom arguments to process

    Returns:
        parsed arguments
    """

    if os.name == 'posix' or 'SHELL' in os.environ:
        env_prefix = 'export '
    elif 'PROMPT' in os.environ:
        env_prefix = 'set '
    else:
        env_prefix = '$env:'

    parser = ArgumentParser(
        prog='cds2md',
        formatter_class=RawDescriptionHelpFormatter,
        description=f'''
A minimal example run:

```
{env_prefix}CDS2MD_CONFLUENCE_TOKEN=TOKEN
{env_prefix}CDS2MD_CONFLUENCE_SPACE_KEY=MYSPACE
{env_prefix}CDS2MD_CONFLUENCE_URL=https://wiki.example.com/
cds2md
```

''',
    )

    parser.add_argument(
        'action',
        nargs='?',
        choices=[a.value for a in Action],
        default=Action.ALL,
        help='action to perform (default: %(default)s)',
    )

    parser.add_argument(
        '--ca-certificate',
        type=parse_file_check,
        default=os.environ.get('CDS2MD_CA_CERTIFICATE'),
        help='ca certificate to use when communicating with Confluence',
    )
    parser.add_argument(
        '--cache',
        type=parse_non_file_path,
        default=Path(CACHE_DIRNAME),
        help='path to store fetch cached data',
    )
    parser.add_argument(
        '--confluence-space-key',
        default=os.environ.get('CDS2MD_CONFLUENCE_SPACE_KEY'),
        help='space to query for pages',
    )
    parser.add_argument(
        '--confluence-token',
        default=os.environ.get('CDS2MD_CONFLUENCE_TOKEN'),
        help='token used to query the Confluence instance',
    )
    parser.add_argument(
        '--confluence-token-file',
        type=parse_file_check,
        help='file which holds a Confluence token to use',
    )
    parser.add_argument(
        '--confluence-token-stdin',
        action='store_true',
        help='pass in the token via the standard input stream',
    )
    parser.add_argument(
        '--confluence-url',
        type=parse_confluence_url,
        default=os.environ.get('CDS2MD_CONFLUENCE_URL'),
        help='url of the Confluence data center instance to interact with',
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='enabling debugging logs',
    )
    parser.add_argument(
        '--development',
        action='store_true',
        help='configure to operate in a development state',
    )
    parser.add_argument(
        '--header',
        '-H',
        type=parse_http_headers,
        action='append',
        help='http headers to include in requests',
    )
    parser.add_argument(
        '--ignore-tls',
        action='store_true',
        help='ignore all TLS checks when communicating with Confluence',
    )
    parser.add_argument(
        '--flat',
        action='store_true',
        help='ignore any Confluence-detected hierarchy structure',
    )
    parser.add_argument(
        '--output',
        type=parse_non_file_path,
        default=Path('output'),
        help='path to output markdown content into',
    )
    parser.add_argument(
        '--timeout',
        type=parse_positive_int,
        default=os.environ.get('CDS2MD_TIMEOUT', DEFAULT_CONNECTION_TIMEOUT),
        help='timeout for connection REST requests to Confluence',
    )
    parser.add_argument(
        '--tweak-admonition-type',
        choices=[at.value for at in AdmonitionType],
        default=AdmonitionType.DEFAULT,
        help='admonition formatting to use (default: %(default)s)',
    )
    parser.add_argument(
        '--tweak-html-images',
        action='store_true',
        help='force all images to be generated as html-based images',
    )
    parser.add_argument(
        '--tweak-html-tables',
        action='store_true',
        help='force all tables to be generated as html-based tables',
    )
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s ' + cds2md_version,
    )
    parser.add_argument(
        '--wrap',
        type=parse_non_negative_int,
        default=DEFAULT_WRAP,
        help='hint to the number of characters to wrap to',
    )

    opts = parser.parse_args(args)

    # post-processing arguments
    if not opts.confluence_url:
        # if not arguments were provided, do a full help output
        if len(sys.argv) <= 1:
            parser.print_help()
            raise SystemExit(1)

        msg = 'confluence url is not configured'
        raise SystemExit(msg)

    if not opts.confluence_space_key:
        msg = 'confluence space key is not configured'
        raise SystemExit(msg)

    if not opts.confluence_token:
        if opts.confluence_token_file:
            content = opts.confluence_token_file.read_text(encoding='utf-8')
            opts.confluence_token = content.strip()
        elif opts.confluence_token_stdin:
            for line in sys.stdin:
                if line.strip():
                    opts.confluence_token = line.strip()

    if not opts.confluence_token:
        msg = 'confluence token is not configured'
        raise SystemExit(msg)

    # merge all header entries into a single dictionary
    if opts.header:
        opts.headers = {k: v for d in opts.header for k, v in d.items()}
    else:
        opts.headers = {}

    # tailor logging state
    if opts.debug:
        # enable utility's debug logs
        logger.setLevel('DEBUG')
        logger_handler.setLevel('DEBUG')

        # enable httpx debug logs
        httpx_logger = logging.getLogger('httpcore')
        httpx_logger.setLevel(logging.DEBUG)
        httpx_logger.propagate = False

        httpx_handler = logging.StreamHandler()
        httpx_handler.setFormatter(logging.Formatter('(httpx) %(message)s'))
        httpx_handler.setLevel(logging.DEBUG)
        httpx_logger.addHandler(httpx_handler)

    # hint that api endpoint does not end with the standard api path
    if 'CDS2MD_IGNORE_URL_API_SUFFIX_CHECK' not in os.environ:
        if not opts.confluence_url.endswith('rest/api'):
            logger.warning('confluence api url does not end with /rest/api')

    return opts


def parse_confluence_url(value: str) -> str:
    """
    parse a raw confluence url

    Validate a user-provided Confluence URL.

    Args:
        value: the raw value

    Returns:
        the confluence url

    Raises:
        ArgumentTypeError if a parsing error occurs
    """

    confluence_url = value.strip('/')

    try:
        parsed_server_name = urlparse(confluence_url)
    except ValueError as exc:
        msg = 'confluence url is not a valid value'
        raise ArgumentTypeError(msg) from exc

    if parsed_server_name.scheme not in ('http', 'https'):
        msg = 'confluence url must start with http(s)://'
        raise ArgumentTypeError(msg)

    if not parsed_server_name.hostname:
        msg = 'confluence url missing a valid hostname'
        raise ArgumentTypeError(msg)

    return confluence_url


def parse_file_check(value: str) -> Path:
    """
    validate a provided path is an existing file

    Validate that a provided path is a file that exists at the time of this
    check.

    Args:
        value: the raw value

    Returns:
        the path value

    Raises:
        ArgumentTypeError if validation fails
    """

    path = Path(value)

    if not path.exists():
        msg = f'{value} does not exist'
        raise ArgumentTypeError(msg)

    if not path.is_file():
        msg = f'{value} is not a file'
        raise ArgumentTypeError(msg)

    return path


def parse_http_headers(value: str) -> dict[str, str]:
    """
    validate a provide string is a header key-value pair

    Validate that a provided string is a header `key: value` string.

    Args:
        value: the raw value

    Returns:
        the path value

    Raises:
        ArgumentTypeError if validation fails
    """

    if ':' not in value:
        msg = f'{value} is an invalid header entry'
        raise ArgumentTypeError(msg)

    key, value = value.split(':', 1)
    key = key.strip()

    if not key:
        msg = f'{value} has an invalid header key'
        raise ArgumentTypeError(msg)

    return {key: value.strip()}


def parse_non_file_path(value: str) -> Path:
    """
    validate a provided path is a possible directory

    Validate that a provided path if a possible directory, where if it exists,
    performs a is-directory check.

    Args:
        value: the raw value

    Returns:
        the path value

    Raises:
        ArgumentTypeError if validation fails
    """

    path = Path(value)

    if path.exists() and not path.is_dir():
        msg = f'{value} is not a directory'
        raise ArgumentTypeError(msg)

    return path


def parse_non_negative_int(value: str) -> int:
    """
    parse a raw non-negative integer value

    Validate a user-provided value that should be a non-negative integer is
    one.

    Args:
        value: the raw value

    Returns:
        the non-negative integer value

    Raises:
        ArgumentTypeError if a parsing error occurs
    """

    try:
        result = int(value)
    except ValueError as exc:
        msg = f'{value} is not a valid integer'
        raise ArgumentTypeError(msg) from exc
    else:
        if result < 0:
            msg = f'{value} is not a non-negative integer'
            raise ArgumentTypeError(msg)

    return result


def parse_positive_int(value: str) -> int:
    """
    parse a raw positive integer value

    Validate a user-provided value that should be a positive integer is
    one.

    Args:
        value: the raw value

    Returns:
        the positive integer value

    Raises:
        ArgumentTypeError if a parsing error occurs
    """

    try:
        result = int(value)
    except ValueError as exc:
        msg = f'{value} is not a valid integer'
        raise ArgumentTypeError(msg) from exc
    else:
        if result < 1:
            msg = f'{value} is not a positive integer'
            raise ArgumentTypeError(msg)

    return result
