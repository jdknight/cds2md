# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorCode(Cds2mdTranslatorTestCase):
    def test_translator_code(self) -> None:
        file = DATA_FOLDER / 'code.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'my `test` example'

        self.assertIn(expected, body)
