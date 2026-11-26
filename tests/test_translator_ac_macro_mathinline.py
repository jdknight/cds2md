# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroMathinline(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_mathinline(self) -> None:
        file = DATA_FOLDER / 'ac_macro_mathinline.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            $E = mc^2$
        ''')

        self.assertIn(expected, body)
