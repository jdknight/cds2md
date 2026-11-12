# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroImage(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_image_default(self) -> None:
        file = DATA_FOLDER / 'ac_macro_image.storage'
        data = file.read_text()

        a2t = {
            ('unit-test', 'test.png'): 'example.png',
        }

        body = self.translate(data, attachment2target=a2t)

        expected = cleandoc('''
            ![](example.png)
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_image_html(self) -> None:
        file = DATA_FOLDER / 'ac_macro_image.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_html_images = True

        a2t = {
            ('unit-test', 'test.png'): 'example.png',
        }

        body = self.translate(data, opts=opts, attachment2target=a2t)

        expected = cleandoc('''
            <img href="example.png" alt="">
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_image_invalid_no_attachment(self) -> None:
        file = DATA_FOLDER / 'ac_macro_image_invalid_no_attachment.storage'
        data = file.read_text()

        body = self.translate(data)

        self.assertNotIn('![]', body)

    def test_translator_ac_macro_image_invalid_no_filename(self) -> None:
        file = DATA_FOLDER / 'ac_macro_image_invalid_no_filename.storage'
        data = file.read_text()

        body = self.translate(data)

        self.assertNotIn('![]', body)

    def test_translator_ac_macro_image_page(self) -> None:
        file = DATA_FOLDER / 'ac_macro_image_page.storage'
        data = file.read_text()

        a2t = {
            ('container/other-page', 'misc.png'): 'container/misc.png',
        }

        t2t = {
            'other-page': 'container/other-page',
            'unit-test': 'container/another-container/unit-test',
        }

        body = self.translate(data, attachment2target=a2t, title2target=t2t)

        expected = cleandoc('''
            ![](../misc.png)
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_image_url(self) -> None:
        file = DATA_FOLDER / 'ac_macro_image_url.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            ![my-alt-text](https://example.com/image.png)
        ''')

        self.assertIn(expected, body)
