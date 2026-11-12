# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroCode(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_code(self) -> None:
        file = DATA_FOLDER / 'ac_macro_code.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            ```python
            this
                is
                    an
            pre
                    example
            ```
        ''')

        self.assertIn(expected, body)
