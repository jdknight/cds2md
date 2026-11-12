# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorBr(Cds2mdTranslatorTestCase):
    def test_translator_br(self) -> None:
        file = DATA_FOLDER / 'br.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            two
            lines
        ''')

        self.assertIn(expected, body)
