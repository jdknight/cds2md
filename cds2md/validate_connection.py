# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from cds2md.logger import logger
import httpx


def validate_connection(opts: Namespace, client: httpx.Client) -> bool:
    confluence_up = False

    try:
        query_api = f'{opts.confluence_url}/server-information'
        rsp = client.get(query_api)
        rsp.raise_for_status()
    except httpx.RequestError as exc:
        logger.error(f'confluence instance not available ({exc})')
    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code
        logger.error(f'confluence instance not available ({code})')
    else:
        confluence_up = True

    return confluence_up
