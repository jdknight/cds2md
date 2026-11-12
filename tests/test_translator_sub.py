# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorSub(Cds2mdTranslatorTestCase):
    def test_translator_sub(self) -> None:
        file = DATA_FOLDER / 'sub.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'my <sub>test</sub> example'

        self.assertIn(expected, body)
