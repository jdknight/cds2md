# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroStatus(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_status(self) -> None:
        file = DATA_FOLDER / 'ac_macro_status.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            **COMPLETED**
        ''')

        self.assertIn(expected, body)
