# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorU(Cds2mdTranslatorTestCase):
    def test_translator_u(self) -> None:
        file = DATA_FOLDER / 'u.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'my <u>test</u> example'

        self.assertIn(expected, body)
