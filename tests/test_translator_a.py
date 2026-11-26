# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorA(Cds2mdTranslatorTestCase):
    def test_translator_a_format(self) -> None:
        file = DATA_FOLDER / 'a_format.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'this is [a \\[formatted\\]](http://example.org/test2) link'

        self.assertIn(expected, body)

    def test_translator_a_simple(self) -> None:
        file = DATA_FOLDER / 'a.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = 'this is [a link](http://example.org/test) to a site'

        self.assertIn(expected, body)
