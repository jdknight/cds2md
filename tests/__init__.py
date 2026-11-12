# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from bs4 import BeautifulSoup
from cds2md.opts import process_options
from cds2md.translator import Translator
from cds2md.translator import TranslatorContext
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from unittest import TestCase
from unittest import TestResult
import errno
import os
import shutil
import tempfile


# folder holding on sample/test data
DATA_FOLDER = Path(__file__).parent / 'data'


class Cds2mdTestCase(TestCase):
    """
    base unit test for all tests
    """

    def run(self, result: TestResult | None = None) -> None:
        """
        run the test

        Run the test, collecting the result into the TestResult object passed as
        result. See `unittest.TestCase.run()` for more details.

        Args:
            result (optional): the test result to populate
        """

        with self.env_wrap():
            super().run(result)

    def build_opts(self) -> Namespace:
        """
        build a standard runtime options

        Help tests to be able to easily generate runtime options.

        Returns:
            the options
        """
        return process_options([
            '--confluence-space-key', 'DUMMY_TEST_SPACE',
            '--confluence-token', 'dummy-token',
            '--confluence-url', 'http://wiki.example.com/rest/api',
        ])

    @contextmanager
    def env_wrap(self) -> Iterator[None]:
        """
        wrap the context's environment

        This context method provides a way restrict environment changes to the
        context.
        """

        old_env = dict(os.environ)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    @contextmanager
    def temp_dir(self, dir_: Path | str | None = None) -> None:
        """
        generate a context-supported temporary directory

        Creates a temporary directory in the provided directory ``dir_`` (or
        system default, is not provided). This is a context-supported call
        and will automatically remove the directory when completed. If the
        provided directory does not exist, it will created.

        Args:
            dir_ (optional): the directory to create the temporary directory in
        """

        if dir_ :
            target = Path(dir_)
            target.mkdir(exist_ok=True)

        dir_ = tempfile.mkdtemp(prefix='.cds2md-tmp-', dir=dir_)
        try:
            yield dir_
        finally:
            try:
                shutil.rmtree(dir_)
            except OSError as e:  # pragma: no cover
                if e.errno != errno.ENOENT:
                    raise

    @contextmanager
    def working_dir(self, dir_: Path | str) -> None:
        """
        move into a context-supported working directory

        Moves the current context into the provided working directory ``dir``.
        When returned, the original working directory will be restored. If the
        provided directory does not exist, it will created.

        Args:
            dir_: the target working directory
        """
        owd = Path.cwd()

        target = Path(dir_)
        target.mkdir(exist_ok=True)

        os.chdir(target)
        try:
            yield target
        finally:
            os.chdir(owd)


class Cds2mdTranslatorTestCase(Cds2mdTestCase):
    """
    tailored test case for translator-specific actions
    """

    def translate(self, data: str,
            attachment2target: dict | None = None,
            opts: Namespace | None = None,
            title2target: dict | None = None,
            ctx: TranslatorContext | None = None) -> str:
        soup = BeautifulSoup(data, 'html.parser')

        if not ctx:
            if not opts:
                opts = self.build_opts()

            ctx = TranslatorContext(
                attachment2target=attachment2target or {},
                opts=opts,
                title2target=title2target or {
                    'unit-test': 'unit-test',
                },
            )

        translator = Translator(ctx, 'unit-test')
        translator.walk(soup)

        return ''.join(translator.output).strip()
