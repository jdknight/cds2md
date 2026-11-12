# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from cds2md.logger import logger
import httpx


def validate_space(opts: Namespace, client: httpx.Client) -> bool:
    space_exists = False

    try:
        fetch_api = f'{opts.confluence_url}/space/{opts.confluence_space_key}'
        rsp = client.get(fetch_api)
        rsp.raise_for_status()
    except httpx.RequestError as exc:
        logger.error(f'confluence instance not available ({exc})')
    except httpx.HTTPStatusError as exc:
        match exc.response.status_code:
            case httpx.codes.UNAUTHORIZED | httpx.codes.FORBIDDEN:
                logger.error('not authenticate with confluence instance')

            case httpx.codes.NOT_FOUND:
                logger.error('space key cannot be found: '
                            f'{opts.confluence_space_key}')

            case _:
                logger.error('unexpected status from confluence instance'
                            f'({exc.response.status_code})')
    else:
        space_exists = True

    return space_exists
