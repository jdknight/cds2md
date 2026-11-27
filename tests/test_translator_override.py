# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from bs4 import Tag
from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase
from cds2md.translator import Translator


class CustomTranslator(Translator):
    def visit_ac_structured_macro(self, node: Tag) -> None:
        macro_type = node.get('ac:name')

        match macro_type:
            case 'custom':
                content = ''
                content_node = node.find('content')
                if content_node:
                    content = content_node.text

                if content:
                    self.append('```custom')
                    self.newline()
                    self.append(f'{content}')
                    self.newline()
                    self.append('```')
                    self.newline(count=2)

                self.skip()

            case _:
                super().visit_ac_structured_macro(node)


class TestTranslatorOverride(Cds2mdTranslatorTestCase):
    def test_translator_override_custom(self) -> None:
        file = DATA_FOLDER / 'ac_macro_custom.storage'
        data = file.read_text()

        body = self.translate(data, translator_cls=CustomTranslator)

        expected = cleandoc('''
            ```custom
            custom
                content
            ```
        ''')

        self.assertEqual(expected, body)

    def test_translator_override_default(self) -> None:
        file = DATA_FOLDER / 'ac_macro_code.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            ```python
            this
                is
                    an
            pre
                    example
            ```
        ''')

        self.assertEqual(expected, body)
