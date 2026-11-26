# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroHtml(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_html(self) -> None:
        file = DATA_FOLDER / 'ac_macro_html.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            <strong>content</strong>
        ''')

        self.assertIn(expected, body)
