# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcInlineCommentMarker(Cds2mdTranslatorTestCase):
    def test_translator_ac_inline_comment_marker(self) -> None:
        file = DATA_FOLDER / 'ac_inline_comment_marker.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            one **two** three
        ''')

        self.assertIn(expected, body)
