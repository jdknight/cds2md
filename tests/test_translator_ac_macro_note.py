# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from cds2md.defs import AdmonitionType
from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroNote(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_note_default_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            # unit-test

            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_default_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note_title.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            > **macro-title**
            >
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_docusaurus_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.DOCUSAURUS

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            :::warning
            macro-content
            :::
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_docusaurus_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.DOCUSAURUS

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            :::warning macro-title
            macro-content
            :::
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_github_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.GITHUB

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > [!WARNING]
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_github_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.GITHUB

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > [!WARNING]
            > **macro-title**
            >
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_gitlab_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.GITLAB

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > [!WARNING]
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_gitlab_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.GITLAB

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > [!WARNING]
            > **macro-title**
            >
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_myst_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.MYST

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            :::{warning}
            macro-content
            :::
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_myst_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.MYST

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            :::{warning}
            **macro-title**

            macro-content
            :::
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_plain_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.PLAIN

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_note_plain_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_note_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.PLAIN

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > **macro-title**
            >
            > macro-content
        ''')

        self.assertIn(expected, body)
