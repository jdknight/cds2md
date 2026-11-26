# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorAcMacroJira(Cds2mdTranslatorTestCase):
    def test_translator_ac_macro_jira_search_no_url(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_search.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            ```jql
            project = "TEST"
            ```
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_jira_search_url(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_search.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.jira_url = 'http://jira.example.com'

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            [Jira Query](http://jira.example.com/issues?project%20%3D%20%22TEST%22)
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_jira_single_no_url(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_single.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            TEST-123
        ''')

        self.assertIn(expected, body)

    def test_translator_ac_macro_jira_single_url(self) -> None:
        file = DATA_FOLDER / 'ac_macro_jira_single.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.jira_url = 'https://www.example.org/tm'

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            [TEST-123](https://www.example.org/tm/browse/TEST-123)
        ''')

        self.assertIn(expected, body)
