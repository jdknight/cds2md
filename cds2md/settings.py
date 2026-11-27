# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight


from cds2md import __version__ as cds2md_version
from cds2md.env import Environment
from cds2md.logger import logger
from inspect import signature
from pathlib import Path
from runpy import run_path
from typing import Any


def load_settings(env: Environment, script: Path) -> None:
    """
    load configuration options from a project settings file (conf.py)

    Provides the ability for users to configure/tweak various options via
    a configuration file.
    """

    globals_: dict[str, Any] | None = {
        'cds2md_version': cds2md_version,
    }

    try:
        raw_settings = run_path(f'{script}', init_globals=globals_)
    except Exception as e:
        logger.exception(f'failed to load configuration: {script}')
        raise Cds2mdInvalidConfigurationError from e

    # if the settings files has a `cds2md_setup` hook for overrides, invoke
    # the setup call
    if 'cds2md_setup' in raw_settings:
        setup_hook = raw_settings['cds2md_setup']
        setup_hook_sig = signature(setup_hook)
        try:
            setup_hook_sig.bind(env)
        except TypeError as e:
            logger.exception('''\
cds2md_setup hook in the project configuration has an invalid signature

When preparing to invoke a project's `cds2md_setup` call, it has been
detected that the call's signature is invalid.''')

            raise Cds2mdInvalidHandlerSignatureError from e
        else:
            try:
                setup_hook(env)
            except Exception as e:
                raise Cds2mdInvalidSetupError from e



class Cds2mdInvalidConfigurationError(Exception):
    """
    exception raised when a setup call has an invalid signature
    """

class Cds2mdInvalidHandlerSignatureError(Exception):
    """
    exception raised when a setup call has an invalid signature
    """


class Cds2mdInvalidSetupError(Exception):
    """
    exception raised when triggering a setup has an issue
    """
