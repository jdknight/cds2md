# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from cds2md.defs import AdmonitionType
from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroWarning(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_warning_default_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_default_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning_title.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            > **macro-title**
            >
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_docusaurus_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.DOCUSAURUS

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            :::caution
            macro-content
            :::
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_docusaurus_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.DOCUSAURUS

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            :::caution macro-title
            macro-content
            :::
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_github_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.GITHUB

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > [!CAUTION]
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_github_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.GITHUB

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > [!CAUTION]
            > **macro-title**
            >
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_gitlab_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.GITLAB

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > [!CAUTION]
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_gitlab_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.GITLAB

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > [!CAUTION]
            > **macro-title**
            >
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_myst_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.MYST

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            :::{caution}
            macro-content
            :::
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_myst_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning_title.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.MYST

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            :::{caution}
            **macro-title**

            macro-content
            :::
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_plain_no_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_admonition_type = AdmonitionType.PLAIN

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            > macro-content
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_warning_plain_title(self) -> None:
        file = DATA_FOLDER / 'ac_macro_warning_title.storage'
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
