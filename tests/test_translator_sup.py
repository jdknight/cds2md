# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorSup(Cds2mdTranslatorTestCase):
    def test_translator_sup(self) -> None:
        file = DATA_FOLDER / 'sup.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'my <sup>test</sup> example'

        self.assertIn(expected, body)
