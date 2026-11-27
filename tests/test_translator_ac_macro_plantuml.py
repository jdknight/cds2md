# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroPlantuml(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_plantuml_html(self) -> None:
        file = DATA_FOLDER / 'ac_macro_plantuml.storage'
        data = file.read_text()

        body = self.translate(data, force_html=True)

        expected = cleandoc('''
            <div class="plantuml">
            @startuml
            Alice -> Bob: Hello
            Bob --> Alice: Hi there!
            @enduml
            </div>
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_plantuml_markdown(self) -> None:
        file = DATA_FOLDER / 'ac_macro_plantuml.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            ```plantuml
            @startuml
            Alice -> Bob: Hello
            Bob --> Alice: Hi there!
            @enduml
            ```
        ''')

        self.assertEqual(expected, body)
