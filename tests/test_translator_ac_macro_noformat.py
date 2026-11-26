# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroNoformat(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_noformat(self) -> None:
        file = DATA_FOLDER / 'ac_macro_noformat.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            ```
            this
                is
                    an
            noformat
                    example
            ```
        ''')

        self.assertIn(expected, body)
