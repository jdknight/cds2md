# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorTime(Cds2mdTranslatorTestCase):
    def test_translator_time_empty(self) -> None:
        file = DATA_FOLDER / 'time_empty.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            2026-11-24
        ''')

        self.assertEqual(expected, body)

    def test_translator_time_value(self) -> None:
        file = DATA_FOLDER / 'time_value.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            Nov 25, 2026
        ''')

        self.assertEqual(expected, body)
