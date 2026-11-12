# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorStrong(Cds2mdTranslatorTestCase):
    def test_translator_b(self) -> None:
        file = DATA_FOLDER / 'b.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'word1 **word2** word3'

        self.assertIn(expected, body)

    def test_translator_strong(self) -> None:
        file = DATA_FOLDER / 'strong.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'word1 **word2** word3'

        self.assertIn(expected, body)
