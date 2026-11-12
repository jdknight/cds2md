# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroLink(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_link_attachment_other(self) -> None:
        file = DATA_FOLDER / 'ac_macro_link_attachment_other.storage'
        data = file.read_text()

        a2t = {
            ('subfolder/another-page', 'example.svg'): 'subfolder/example.svg',
        }

        t2t = {
            'another-page': 'subfolder/another-page',
            'unit-test': 'unit-test',
        }

        body = self.translate(data, attachment2target=a2t, title2target=t2t)

        expected = cleandoc('''
            [](subfolder/example.svg)
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_link_attachment_self(self) -> None:
        file = DATA_FOLDER / 'ac_macro_link_attachment_self.storage'
        data = file.read_text()

        a2t = {
            ('unit-test', 'example42.svg'): 'example42.svg',
        }

        t2t = {
            'unit-test': 'unit-test',
        }

        body = self.translate(data, attachment2target=a2t, title2target=t2t)

        expected = cleandoc('''
            [](example42.svg)
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_link_page_child(self) -> None:
        file = DATA_FOLDER / 'ac_macro_link_page.storage'
        data = file.read_text()

        t2t = {
            'other-page': 'container/another-container/other-page',
            'unit-test': 'container/unit-test',
        }

        body = self.translate(data, title2target=t2t)

        expected = cleandoc('''
            [](another-container/other-page)
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_link_page_parent(self) -> None:
        file = DATA_FOLDER / 'ac_macro_link_page.storage'
        data = file.read_text()

        t2t = {
            'other-page': 'container/other-page',
            'unit-test': 'container/another-container/unit-test',
        }

        body = self.translate(data, title2target=t2t)

        expected = cleandoc('''
            [](../other-page)
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_link_page_sibling(self) -> None:
        file = DATA_FOLDER / 'ac_macro_link_page.storage'
        data = file.read_text()

        t2t = {
            'other-page': 'container/other-page',
            'unit-test': 'container/unit-test',
        }

        body = self.translate(data, title2target=t2t)

        expected = cleandoc('''
            [](other-page)
        ''')

        self.assertIn(expected, body)
