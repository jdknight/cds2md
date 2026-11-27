# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorEm(Cds2mdTranslatorTestCase):
    def test_translator_em_html(self) -> None:
        file = DATA_FOLDER / 'em.storage'
        data = file.read_text()

        body = self.translate(data, force_html=True)

        expected = 'an <em>example</em> emphasis'

        self.assertEqual(expected, body)

    def test_translator_em_markdown(self) -> None:
        file = DATA_FOLDER / 'em.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'an *example* emphasis'

        self.assertEqual(expected, body)
