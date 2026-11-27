# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

import re


def escape_markdown(value: str, *, newline: bool = False) -> str:
    """
    escape text for markdown input

    Accepts text that should be added in a Markdown document that escapes any
    Markdown.

    Args:
        value: the value to escape
        newline (optional): whether the value occurs on a newline

    Returns:
        the escaped content
    """

    # always escape asterisks, backslashes, backticks and tildes
    value = re.sub(r'([*\\`~])', r'\\\1', value)

    # escape underscores at word boundaries
    value = re.sub(r'(?<!\w)_|_(?!\w)', r'\_', value)

    # escape brackets for reference/image syntax
    value = re.sub(r'(!?)\[([^\]]*)\](?=[\(\[])', r'\1\\[\2\\]', value)

    # escapes that only apply to newlines
    if newline:
        # blockquotes, headers and unordered lists
        value = re.sub(r'^(\s{0,3})([>#\-+])', r'\1\\\2', value)

        # ordered lists
        value = re.sub(r'^(\s{0,3})(\d+)([.)])', r'\1\2\\\3', value)

    return value
