# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorImg(Cds2mdTranslatorTestCase):
    def test_translator_img_html(self) -> None:
        file = DATA_FOLDER / 'img.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_html_images = True

        body = self.translate(data, opts=opts)

        expected = '<img height="100" src="pic.png" width="200"/>'

        self.assertEqual(expected, body)

    def test_translator_img_markdown(self) -> None:
        file = DATA_FOLDER / 'img.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = '![](pic.png)'

        self.assertEqual(expected, body)
