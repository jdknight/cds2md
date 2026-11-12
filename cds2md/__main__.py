# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from cds2md.engine import engine
from cds2md.logger import logger
from cds2md.opts import process_options


def main() -> None:
    """
    publish helper mainline

    The mainline for cds2md's publisher helper utility.
    """

    # process command line/environment options
    opts = process_options()

    # if running a debugging, output the configuration used
    if opts.debug:
        debug_opts = vars(opts).copy()

        # sanitize options which may expose token/etc. information
        if debug_opts.get('confluence_token'):
            debug_opts['confluence_token'] = '(set)'  # noqa: S105
        if debug_opts.get('header'):
            debug_opts['header'] = '(set)'
        if debug_opts.get('headers'):
            debug_opts['headers'] = '(set)'

        # pretty paths
        debug_opts['cache'] = debug_opts['cache'].as_posix() + '/'
        debug_opts['output'] = debug_opts['output'].as_posix() + '/'

        logger.debug(f'configuration: {debug_opts}')

    # run the utility
    engine(opts)


if __name__ == '__main__':
    main()  # pragma: no cover
