# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAnchor(Cds2mdTranslatorTestCase):
    def test_translator_anchor_html(self) -> None:
        file = DATA_FOLDER / 'anchor.storage'
        data = file.read_text()

        anchor_ids = {
            'unit-test': {'myref'},
        }

        body = self.translate(data, anchor_ids=anchor_ids, force_html=True)

        expected = cleandoc('''
            <p><span id="myref"></span></p>
            <p><a href="#myref">[CITREF1]</a></p>
            <p><a href="#myref">[CITREF2]</a></p>
        ''')

        self.assertEqual(expected, body)

    def test_translator_anchor_markdown(self) -> None:
        file = DATA_FOLDER / 'anchor.storage'
        data = file.read_text()

        anchor_ids = {
            'unit-test': {'myref'},
        }

        body = self.translate(data, anchor_ids=anchor_ids)

        expected = cleandoc('''
            <span id="myref"></span>

            [[CITREF1]](#myref)

            [[CITREF2]](#myref)
        ''')

        self.assertEqual(expected, body)
