# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorPre(Cds2mdTranslatorTestCase):
    def test_translator_pre(self) -> None:
        file = DATA_FOLDER / 'pre.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            ```
            this
                is
                    an
            pre
                    example
            ```
        ''')

        self.assertIn(expected, body)
