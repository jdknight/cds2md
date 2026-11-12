# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorHr(Cds2mdTranslatorTestCase):
    def test_translator_hr(self) -> None:
        file = DATA_FOLDER / 'hr.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = '---'

        self.assertIn(expected, body)
