# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorS(Cds2mdTranslatorTestCase):
    def test_translator_s_html(self) -> None:
        file = DATA_FOLDER / 's.storage'
        data = file.read_text()

        body = self.translate(data, force_html=True)

        expected = 'an <s>example</s> strikethrough'

        self.assertIn(expected, body)

    def test_translator_s_markdown(self) -> None:
        file = DATA_FOLDER / 's.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'an ~~example~~ strikethrough'

        self.assertIn(expected, body)
