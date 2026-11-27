# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from cds2md.util import escape_markdown as escape
from tests import Cds2mdTranslatorTestCase


class TestEscaping(Cds2mdTranslatorTestCase):
    def test_escaping_asterisks(self) -> None:
        escaped = escape(r'some *content* to han**d**le')
        expected = r'some \*content\* to han\*\*d\*\*le'

        self.assertEqual(escaped, expected)

    def test_escaping_backslashes(self) -> None:
        escaped = escape(r'some \backslas\h entries')
        expected = r'some \\backslas\\h entries'

        self.assertEqual(escaped, expected)

    def test_escaping_backticks(self) -> None:
        escaped = escape(r'my`code`content')
        expected = r'my\`code\`content'

        self.assertEqual(escaped, expected)

    def test_escaping_blockquotes_change(self) -> None:
        escaped = escape(r'> content', newline=True)
        expected = r'\> content'

        self.assertEqual(escaped, expected)

    def test_escaping_blockquotes_nochange(self) -> None:
        escaped = escape(r'> content')
        expected = r'> content'

        self.assertEqual(escaped, expected)

    def test_escaping_headers_change(self) -> None:
        escaped = escape(r'# header', newline=True)
        expected = r'\# header'

        self.assertEqual(escaped, expected)

    def test_escaping_headers_nochange(self) -> None:
        escaped = escape(r'# header')
        expected = r'# header'

        self.assertEqual(escaped, expected)

    def test_escaping_ordered_list_dot_change(self) -> None:
        escaped = escape(r'1. entry', newline=True)
        expected = r'1\. entry'

        self.assertEqual(escaped, expected)

    def test_escaping_ordered_list_dot_nochange(self) -> None:
        escaped = escape(r'1. entry')
        expected = r'1. entry'

        self.assertEqual(escaped, expected)

    def test_escaping_ordered_list_parenthesis_change(self) -> None:
        escaped = escape(r'1) entry', newline=True)
        expected = r'1\) entry'

        self.assertEqual(escaped, expected)

    def test_escaping_ordered_list_parenthesis_nochange(self) -> None:
        escaped = escape(r'1) entry')
        expected = r'1) entry'

        self.assertEqual(escaped, expected)

    def test_escaping_unordered_list_dash_change(self) -> None:
        escaped = escape(r'- entry', newline=True)
        expected = r'\- entry'

        self.assertEqual(escaped, expected)

    def test_escaping_unordered_list_dash_nochange(self) -> None:
        escaped = escape(r'- entry')
        expected = r'- entry'

        self.assertEqual(escaped, expected)

    def test_escaping_unordered_list_plus_change(self) -> None:
        escaped = escape(r'+ entry', newline=True)
        expected = r'\+ entry'

        self.assertEqual(escaped, expected)

    def test_escaping_unordered_list_plus_nochange(self) -> None:
        escaped = escape(r'+ entry')
        expected = r'+ entry'

        self.assertEqual(escaped, expected)

    def test_escaping_hr_check1(self) -> None:
        escaped = escape(r'---', newline=True)
        expected = r'\---'

        self.assertEqual(escaped, expected)

    def test_escaping_hr_check2(self) -> None:
        escaped = escape(r'- - -', newline=True)
        expected = r'\- - -'

        self.assertEqual(escaped, expected)

    def test_escaping_hr_check3(self) -> None:
        escaped = escape(r'___', newline=True)
        expected = r'\__\_'

        self.assertEqual(escaped, expected)

    def test_escaping_hr_check4(self) -> None:
        escaped = escape(r'_ _ _', newline=True)
        expected = r'\_ \_ \_'

        self.assertEqual(escaped, expected)

    def test_escaping_hr_check5(self) -> None:
        escaped = escape(r'***', newline=True)
        expected = r'\*\*\*'

        self.assertEqual(escaped, expected)

    def test_escaping_hr_check6(self) -> None:
        escaped = escape(r'* * *', newline=True)
        expected = r'\* \* \*'

        self.assertEqual(escaped, expected)

    def test_escaping_hr_nochange(self) -> None:
        escaped = escape(r'my~tilde~content')
        expected = r'my\~tilde\~content'

        self.assertEqual(escaped, expected)

    def test_escaping_tildes(self) -> None:
        escaped = escape(r'my~tilde~content')
        expected = r'my\~tilde\~content'

        self.assertEqual(escaped, expected)

    def test_escaping_underscores_href(self) -> None:
        escaped = escape(r'[Link Text](https://example.com)')
        expected = r'\[Link Text\](https://example.com)'

        self.assertEqual(escaped, expected)

    def test_escaping_underscores_image(self) -> None:
        escaped = escape(r'![](img.png)')
        expected = r'!\[\](img.png)'

        self.assertEqual(escaped, expected)

    def test_escaping_underscores_nochange(self) -> None:
        escaped = escape(r'my [bracketed] content')
        expected = r'my [bracketed] content'

        self.assertEqual(escaped, expected)
