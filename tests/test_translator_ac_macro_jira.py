# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroJira(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_jira_search_no_url_html(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_search.storage'
        data = file.read_text()

        body = self.translate(data, force_html=True)

        expected = cleandoc('''
            <pre>
            project = "TEST"
            </pre>
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_search_no_url_markdown(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_search.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            ```jql
            project = "TEST"
            ```
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_search_url_html(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_search.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.jira_url = 'http://jira.example.com'

        body = self.translate(data, opts=opts, force_html=True)

        expected_url = f'{opts.jira_url}/issues/?jql=project%20%3D%20%22TEST%22'
        expected = cleandoc(f'''
            <a href="{expected_url}">Jira Query</a>
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_search_url_markdown(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_search.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.jira_url = 'http://jira.example.com'

        body = self.translate(data, opts=opts)

        expected = cleandoc(f'''
            [Jira Query]({opts.jira_url}/issues/?jql=project%20%3D%20%22TEST%22)
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_single_nosummary_no_url(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_single_nosummary.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            TEST-123
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_single_summary_no_url(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_single_summary.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            TEST-123
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_single_nosummary_url_html(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_single_nosummary.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.jira_url = 'https://www.example.org/tm'

        body = self.translate(data, opts=opts, force_html=True)

        expected = cleandoc(f'''
            <a href="{opts.jira_url}/browse/TEST-123">TEST-123</a>
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_single_nosummary_url_markdown(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_single_nosummary.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.jira_url = 'https://www.example.org/tm'

        body = self.translate(data, opts=opts)

        expected = cleandoc(f'''
            [TEST-123]({opts.jira_url}/browse/TEST-123)
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_single_summary_url_html(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_single_summary.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.jira_url = 'https://www.example.org/tm'

        jira2summary = {
            'TEST-123': 'Example Summary',
        }

        body = self.translate(
            data,
            force_html=True,
            jira2summary=jira2summary,
            opts=opts,
        )

        expected = cleandoc(f'''
            <a href="{opts.jira_url}/browse/TEST-123">TEST-123</a>: Example Summary
        ''')

        self.assertEqual(expected, body)

    def test_translator_ac_macro_jira_single_summary_url_markdown(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_single_summary.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.jira_url = 'https://www.example.org/tm'

        jira2summary = {
            'TEST-123': 'Example Summary',
        }

        body = self.translate(data, opts=opts, jira2summary=jira2summary)

        expected = cleandoc(f'''
            [TEST-123]({opts.jira_url}/browse/TEST-123): Example Summary
        ''')

        self.assertEqual(expected, body)
