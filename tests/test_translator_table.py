# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from inspect import cleandoc
from tests import DATA_FOLDER
from tests import Cds2mdTranslatorTestCase


class TestTranslatorTable(Cds2mdTranslatorTestCase):
    def test_translator_table_html(self) -> None:
        file = DATA_FOLDER / 'table.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_html_tables = True

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            <table>
             <thead>
              <tr><th>a</th><th>b</th></tr>
             </thead>
             <tbody>
              <tr><td>1</td><td>2</td></tr>
              <tr><td>3</td><td>4</td></tr>
             </tbody>
            </table>
        ''')

        self.assertIn(expected, body)

    def test_translator_table_inlined_tags(self) -> None:
        file = DATA_FOLDER / 'table_inlined_tags.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_html_tables = True

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            <table>
             <thead>
              <tr><th>a</th></tr>
             </thead>
             <tbody>
              <tr><td><a href="example.com">example</a></td></tr>
              <tr><td><br></td></tr>
              <tr><td><code>test</code></td></tr>
              <tr><td><dl><dt>b1</dt><dd>b2</dd><dt>b3</dt><dd>b4</dd></dl></td></tr>
              <tr><td><em>test</em></td></tr>
              <tr><td><h1>test</h1><h2>test</h2><h3>test</h3><h4>test</h4><h5>test</h5><h6>test</h6></td></tr>
              <tr><td><hr>

            test</td></tr>
              <tr><td><ol><li>1</li><li>2</li><li>3</li><li>4</li></ol></td></tr>
              <tr><td><p>text</p></td></tr>
              <tr><td><pre>
            my
                content
            </pre>
            </td></tr>
              <tr><td><strong>test</strong></td></tr>
              <tr><td><sub>test</sub></td></tr>
              <tr><td><sup>test</sup></td></tr>
              <tr><td><ul><li>1</li><li>2</li><li>3</li><li>4</li></ul></td></tr>
              <tr><td></td></tr>
             </tbody>
            </table>

        ''')

        self.assertIn(expected, body)

    def test_translator_table_multiple_thead_rows(self) -> None:
        file = DATA_FOLDER / 'table_multiple_thead_rows.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            <table>
             <thead>
              <tr><th>a</th><th>b</th></tr>
              <tr><th>c</th><th>d</th></tr>
             </thead>
             <tbody>
              <tr><td>1</td><td>2</td></tr>
              <tr><td>3</td><td>4</td></tr>
             </tbody>
            </table>
        ''')

        self.assertIn(expected, body)

    def test_translator_table_nested(self) -> None:
        file = DATA_FOLDER / 'table_nested.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            <table>
             <thead>
              <tr><th>a</th><th>b</th></tr>
             </thead>
             <tbody>
              <tr><td>1</td><td>2</td></tr>
              <tr><td>3</td><td><table>
             <thead>
              <tr><th>c</th><th>d</th></tr>
             </thead>
             <tbody>
              <tr><td>4</td><td>5</td></tr>
              <tr><td>6</td><td>7</td></tr>
             </tbody>
            </table>
            </td></tr>
             </tbody>
            </table>
        ''')

        self.assertIn(expected, body)

    def test_translator_table_no_thead(self) -> None:
        file = DATA_FOLDER / 'table_no_thead.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            | | |
            | - | - |
            | 1 | 2 |
            | 3 | 4 |
        ''')

        self.assertIn(expected, body)

    def test_translator_table_simple(self) -> None:
        file = DATA_FOLDER / 'table.storage'
        data = file.read_text()

        body = self.translate(data)

        expected = cleandoc('''
            | a | b |
            | - | - |
            | 1 | 2 |
            | 3 | 4 |
        ''')

        self.assertIn(expected, body)

    def test_translator_table_spans(self) -> None:
        file = DATA_FOLDER / 'table_spans.storage'
        data = file.read_text()

        opts = self.build_opts()
        opts.tweak_html_tables = True

        body = self.translate(data, opts=opts)

        expected = cleandoc('''
            <table>
             <thead>
              <tr><th>a</th><th>b</th></tr>
             </thead>
             <tbody>
              <tr><td>1</td><td rowspan="2">2</td></tr>
              <tr><td>3</td></tr>
              <tr><td colspan="2">4</td></tr>
             </tbody>
            </table>
        ''')

        self.assertIn(expected, body)
