# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorDl(Cds2mdTranslatorTestCase):
    def test_translator_dl(self) -> None:
        file = DATA_FOLDER / 'dl.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            **one**

            two

            **three**

            **four**

            five
        ''')

        self.assertIn(expected, body)
