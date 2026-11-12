# SPDX-License-Identifier: BSD-2-Clause
# Copyright jdknight

from argparse import Namespace
from bs4 import NavigableString
from bs4 import PageElement
from bs4 import Tag
from cds2md.defs import AdmonitionType
from cds2md.logger import logger
from dataclasses import dataclass
from pathlib import Path
from typing import cast
import os
import re
import textwrap


@dataclass
class TranslatorContext:
    attachment2target: dict
    opts: Namespace
    title2target: dict


class Translator:
    def __init__(self, ctx: TranslatorContext, title: str) -> None:
        self.output = [
            # always lead new documents with their title name, which is
            # pulled from Confluence's metadata and not in a page's body
            f'# {title}\n\n',
        ]

        self.admonition_prefix_context = [False]
        self.admonition_prefix_pending = False
        self.admonition_type = ctx.opts.tweak_admonition_type
        self.attachment2target = ctx.attachment2target
        self.html_mode_context = [False]
        self.indent_context: list[str] = []
        self.indent_offset = [0]
        self.opts = ctx.opts
        self.output_context: list[list[str]] = []
        self.preserve_whitespace = True
        self.title = title
        self.title2target = ctx.title2target

    def walk(self, node: PageElement) -> None:
        if isinstance(node, Tag):
            try:
                self.dispatch_visit(node)

                for child in node.children:
                    self.walk(child)

                self.dispatch_depart(node)

            # if a node is completed or not applicable, we will ignore it
            except SkipNode:
                pass
        elif isinstance(node, NavigableString):
            self.visit_text(node)

    def dispatch_visit(self, node: Tag) -> None:
        name = self._tag_name(node)
        getattr(self, f'visit_{name}', self.unknown_visit)(node)

    def dispatch_depart(self, node: Tag) -> None:
        name = self._tag_name(node)
        getattr(self, f'depart_{name}', self.unknown_depart)(node)

    def _tag_name(self, node: Tag) -> str:
        # Simplify tag names when trying to map to a method:
        # - Help `ac:link` to be `ac_link`
        # - Handle `[document]` from bs4
        return re.sub(r'[^a-z0-9]', '_', node.name.strip('[]').lower())

    def visit_text(self, node: NavigableString) -> None:
        # ignore empty text entries, except if we are adding a space between
        # tags
        if not node.strip() and node != ' ':
            return

        node_text = str(node)

        # reduce the wrap if we are indenting any text contents
        wrap = max(self.opts.wrap - self.indent_offset[-1], 0)

        # check if we are configured to wrap content
        if wrap > 0:
            # track any leading/trailing whitespace content, which we want to
            # restore to ensure proper inline spacing between elements
            lead = ' ' if node_text[0].isspace() else ''
            tail = ' ' if node_text[-1].isspace() else ''

            node_text = ' '.join(node_text.split())

            node_text = textwrap.fill(
                node_text,
                break_long_words=False,
                break_on_hyphens=False,
                width=wrap,
            )

            # restore leading/trailing whitespace for inlined content; but
            # skip if we are in a context that wants to skip it
            if self.preserve_whitespace:
                node_text = f'{lead}{node_text}{tail}'

        # check if we should indent this text content
        indent = ' ' * self.indent_offset[-1]
        if indent and node.strip():
            last_ends_with_nl = self.output[-1].endswith('\n')
            if last_ends_with_nl:
                node_text = f'{indent}{node_text}'
            node_text = f'\n{indent}'.join(node_text.splitlines())

        self._append(node_text)

        # ensure re-flag preserving whitespaces after processing text
        self.preserve_whitespace = True

    def visit_a(self, node: Tag) -> None:
        if self._is_html_mode():
            href = node.get('href', '')
            self._append(f'<a href="{href}">')
        else:
            self._append('[')

    def depart_a(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</a>')
        else:
            href = node.get('href', '')
            self._append(f']({href})')

    def visit_ac_image(self, node: Tag) -> None:
        attachment_url = node.find('ri:url', recursive=False)
        if attachment_url:
            alt = cast('str', node.get('ac:alt', ''))
            href = cast('str', attachment_url.get('ri:value', '#'))
            self._build_image(href, alt)
            raise SkipNode

        attachment_node = node.find('ri:attachment', recursive=False)
        if not attachment_node:
            logger.warning('unexpected ac:image with no ri:attachment')
            raise SkipNode

        attachment_filename = attachment_node.get('ri:filename')
        if not attachment_filename:
            logger.warning('unexpected ac:image with no attachment filename')
            raise SkipNode

        # check if this attachment is hosted from another page
        attachment_page = attachment_node.find('ri:page', recursive=False)
        if attachment_page:
            page_title = attachment_page.get('ri:content-title', '')
            page_slug = self.title2target.get(page_title)
        else:
            page_slug = self.title2target.get(self.title)

        if not page_slug:
            logger.warning(f'unable to find attachment origin: {self.title}')
            raise SkipNode

        key = (page_slug, attachment_filename)
        attachment_ref = self.attachment2target.get(key)
        if not attachment_ref:
            logger.warning(f'unexpected image with no mapped attachment: {key}')
            raise SkipNode

        alt = cast('str', node.get('alt', ''))
        resolved_ref = self._resolve_ref(attachment_ref)
        self._build_image(resolved_ref, alt)
        raise SkipNode

    def _build_image(self, href: str, alt: str) -> None:
        if self._is_html_mode() or self.opts.tweak_html_images:
            self._append(f'<img href="{href}" alt="{alt}">')
        else:
            self._append(f'![{alt}]({href})')

    def visit_ac_layout(self, node: Tag) -> None:
        pass

    def depart_ac_layout(self, node: Tag) -> None:
        pass

    def visit_ac_layout_section(self, node: Tag) -> None:
        pass

    def depart_ac_layout_section(self, node: Tag) -> None:
        pass

    def visit_ac_layout_cell(self, node: Tag) -> None:
        pass

    def depart_ac_layout_cell(self, node: Tag) -> None:
        pass

    def visit_ac_link(self, node: Tag) -> None:
        if self._is_html_mode():
            href = self._resolve_ac_link_href(node)
            self._append(f'<a href="{href}">')
        else:
            self._append('[')

    def depart_ac_link(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</a>')
        else:
            href = self._resolve_ac_link_href(node)
            self._append(f']({href})')

    def _depart_ac_link_attachment(self, node: Tag) -> str:
        attachment_node = node.find('ri:attachment', recursive=False)
        assert attachment_node

        attachment_filename = attachment_node.get('ri:filename')
        if not attachment_filename:
            logger.warning('unexpected ac:link with no attachment filename')
            raise SkipNode

        # check if this attachment is hosted from another page
        attachment_page = attachment_node.find('ri:page', recursive=False)
        if attachment_page:
            page_title = attachment_page.get('ri:content-title', '')
            page_slug = self.title2target.get(page_title)
        else:
            page_slug = self.title2target.get(self.title)

        if not page_slug:
            logger.warning(f'unable to find attachment origin: {self.title}')
            raise SkipNode

        key = (page_slug, attachment_filename)
        attachment_ref = self.attachment2target.get(key)
        if not attachment_ref:
            logger.warning(f'unexpected link with no mapped attachment: {key}')
            raise SkipNode

        return self._resolve_ref(attachment_ref)

    def _depart_ac_link_anchor(self, node: Tag) -> str:
        return cast('str', node.get('ac:anchor', '#'))

    def _depart_ac_link_page(self, node: Tag) -> str:
        page_ref_node = node.find('ri:page', recursive=False)
        assert page_ref_node
        target_title = page_ref_node.get('ri:content-title')
        page_slug = self.title2target.get(target_title, '#')
        return self._resolve_ref(page_slug)

    def _resolve_ac_link_href(self, node: Tag) -> str:
        if 'ac:anchor' in node:
            href = self._depart_ac_link_anchor(node)
        elif node.find('ri:page', recursive=False):
            href = self._depart_ac_link_page(node)
        elif node.find('ri:attachment', recursive=False):
            href = self._depart_ac_link_attachment(node)
        else:
            href = '#'

        return href

    def visit_ac_link_body(self, node: Tag) -> None:
        pass

    def depart_ac_link_body(self, node: Tag) -> None:
        pass

    def visit_ac_parameter(self, node: Tag) -> None:
        raise SkipNode

    def visit_ac_plain_text_link_body(self, node: Tag) -> None:
        pass

    def depart_ac_plain_text_link_body(self, node: Tag) -> None:
        pass

    def visit_ac_rich_text_body(self, node: Tag) -> None:
        pass

    def depart_ac_rich_text_body(self, node: Tag) -> None:
        pass

    def visit_ac_structured_macro(self, node: Tag) -> None:
        macro_type = node.get('ac:name')
        if not macro_type:
            logger.warning('unexpected structured macro with no name')
            raise SkipNode

        match macro_type:
            case 'anchor':
                anchor_id = None
                parameter_node = node.find('ac:parameter')
                if parameter_node:
                    anchor_id = parameter_node.text

                if anchor_id:
                    # not (yet?) implemented
                    logger.debug(f'ignoring anchor: {anchor_id}')
                else:
                    logger.warning('ignored empty anchor')

                raise SkipNode

            case 'code':
                code_language = ''
                lang_node = node.find('ac:parameter', {'ac:name': 'language'})
                if lang_node:
                    code_language = lang_node.text

                code_data = ''
                code_data_node = node.find('ac:plain-text-body')
                if code_data_node:
                    code_data = code_data_node.text

                self._append(f'```{code_language}\n{code_data}\n```\n\n')
                raise SkipNode

            case 'info' | 'note' | 'tip' | 'warning':
                admonition_title = ''
                title_append = ''
                title_node = node.find('ac:parameter', {'ac:name': 'title'})
                if title_node:
                    admonition_title = title_node.text
                    if admonition_title:
                        title_append = f' {admonition_title}'

                match macro_type:
                    case 'info':
                        match self.admonition_type:
                            case AdmonitionType.DOCUSAURUS:
                                self._append(f':::note{title_append}')
                            case AdmonitionType.GITHUB | AdmonitionType.GITLAB:
                                self._append('> [!NOTE]')
                            case AdmonitionType.MYST:
                                self._append(':::{note}')
                    case 'note':
                        match self.admonition_type:
                            case AdmonitionType.DOCUSAURUS:
                                self._append(f':::warning{title_append}')
                            case AdmonitionType.GITHUB | AdmonitionType.GITLAB:
                                self._append('> [!WARNING]')
                            case AdmonitionType.MYST:
                                self._append(':::{warning}')
                    case 'tip':
                        match self.admonition_type:
                            case AdmonitionType.DOCUSAURUS:
                                self._append(f':::tip{title_append}')
                            case AdmonitionType.GITHUB | AdmonitionType.GITLAB:
                                self._append('> [!TIP]')
                            case AdmonitionType.MYST:
                                self._append(':::{tip}')
                    case 'warning':
                        match self.admonition_type:
                            case AdmonitionType.DOCUSAURUS:
                                self._append(f':::caution{title_append}')
                            case AdmonitionType.GITHUB | AdmonitionType.GITLAB:
                                self._append('> [!CAUTION]')
                            case AdmonitionType.MYST:
                                self._append(':::{caution}')

                # track if this type of admonition will be prefixed with ">"
                is_admonition_prefixed = False

                match self.admonition_type:
                    case str() if self.admonition_type in {
                        AdmonitionType.DEFAULT,
                        AdmonitionType.GITHUB,
                        AdmonitionType.GITLAB,
                        AdmonitionType.PLAIN,
                    }:
                        is_admonition_prefixed = True

                self.admonition_prefix_context.append(is_admonition_prefixed)

                # with an exception for non-title-leading admonitions, add a
                # newline after registering the admonition entry, which is
                # done after we have configured admonition_prefix_context
                match self.admonition_type:
                    case str() if self.admonition_type not in {
                        AdmonitionType.DEFAULT,
                        AdmonitionType.PLAIN,
                    }:
                        self._newline()

                # include any admonition title (if supported)
                if self.admonition_type != AdmonitionType.DOCUSAURUS:
                    if admonition_title:
                        self._append(f'**{admonition_title}**')
                        self._newline(count=2)

            # unsupported macros (no content skip)
            case str() if macro_type in {  # noqa: FURB171
                'expand',
            }:
                logger.warning(f'ignored unsupported macro {macro_type}')

            # unsupported macros (content skip)
            case str() if macro_type in {
                'children',
                'roadmap',
                'view-file',
            }:
                logger.warning(f'ignored unsupported macro {macro_type}')
                raise SkipNode

            case _:
                if self.opts.development:
                    logger.error(f'unknown confluence macro {macro_type}')
                    logger.error(node)
                    raise SystemExit

                logger.warning(f'unknown confluence macro {macro_type}')
                raise SkipNode

    def depart_ac_structured_macro(self, node: Tag) -> None:
        macro_type = node.get('ac:name')
        assert macro_type

        match macro_type:
            case 'info' | 'note' | 'tip' | 'warning':
                self.output[-1] = self.output[-1].rstrip('\n')

                match self.admonition_type:
                    case AdmonitionType.DOCUSAURUS | AdmonitionType.MYST:
                        self._append(':::')
                        self._newline(count=2)

                was_admonition_prefixed = self.admonition_prefix_context.pop()
                if was_admonition_prefixed and self.admonition_prefix_pending:
                    self.output.pop()
                    self._newline()

    def visit_br(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<br>')
        else:
            self._newline()

        raise SkipNode

    def visit_code(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<code>')
        else:
            self._append(f'`{node.text}`')
            raise SkipNode

    def depart_code(self, node: Tag) -> None:
        assert self._is_html_mode()
        self._append('</code>')

    def visit_colgroup(self, node: Tag) -> None:
        raise SkipNode

    def visit_div(self, node: Tag) -> None:
        pass

    def depart_div(self, node: Tag) -> None:
        self._newline()

    def visit_document(self, node: Tag) -> None:
        pass

    def depart_document(self, node: Tag) -> None:
        pass

    def visit_dd(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<dd>')

    def depart_dd(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</dd>')
        else:
            self._newline(count=2)

    def visit_dl(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<dl>')

    def depart_dl(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</dl>')

    def visit_dt(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<dt>')
        else:
            self._append('**')

    def depart_dt(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</dt>')
        else:
            self._append('**')
            self._newline(count=2)

    def visit_li(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<li>')
        else:
            indent = '-' if self.indent_context[-1] == 'ul' else '1.'
            offset = ' ' * self.indent_offset[-2]
            self._append(f'{offset}{indent} ')

            self.preserve_whitespace = False

    def depart_li(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</li>')
        else:
            self._newline()

    def visit_em(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<em>')
        else:
            self._append('*')

    def depart_em(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</em>')
        else:
            self._append('*')

    def visit_h1(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<h1>')
        else:
            self._append('# ')

    def depart_h1(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</h1>')
        else:
            self._newline(count=2)

    def visit_h2(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<h2>')
        else:
            self._append('## ')

    def depart_h2(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</h2>')
        else:
            self._newline(count=2)

    def visit_h3(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<h3>')
        else:
            self._append('### ')

    def depart_h3(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</h3>')
        else:
            self._newline(count=2)

    def visit_h4(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<h4>')
        else:
            self._append('#### ')

    def depart_h4(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</h4>')
        else:
            self._newline(count=2)

    def visit_h5(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<h5>')
        else:
            self._append('##### ')

    def depart_h5(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</h5>')
        else:
            self._newline(count=2)

    def visit_h6(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<h6>')
        else:
            self._append('###### ')

    def depart_h6(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</h6>')
        else:
            self._newline(count=2)

    def visit_hr(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<hr>')
        else:
            self._append('---')

        self._newline(count=2)
        raise SkipNode

    def visit_ol(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<ol>')
        else:
            self.indent_context.append('ol')
            self.indent_offset.append(self.indent_offset[-1] + 3)

    def depart_ol(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</ol>')
        else:
            self.indent_context.pop()
            self.indent_offset.pop()
            self._newline()

    def visit_p(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<p>')

    def depart_p(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</p>')
        elif self.indent_offset[-1] == 0:
            self._newline(count=2)

    def visit_pre(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<pre>')
        else:
            self._append('```')
        self._newline()
        self._append(f'{node.text.strip()}')
        self._newline()
        if self._is_html_mode():
            self._append('</pre>')
        else:
            self._append('```')
        self._newline(count=2)
        raise SkipNode

    def visit_ri_attachment(self, node: Tag) -> None:
        raise SkipNode

    def visit_ri_page(self, node: Tag) -> None:
        raise SkipNode

    def visit_span(self, node: Tag) -> None:
        span_class = cast('str', node.get('class', ''))

        # ignore any aui icons
        if 'aui-icon' in span_class:
            raise SkipNode

    def depart_span(self, node: Tag) -> None:
        pass

    def visit_strong(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<strong>')
        else:
            self._append('**')

    def depart_strong(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</strong>')
        else:
            self._append('**')

    visit_b = visit_strong
    depart_b = depart_strong

    def visit_sub(self, node: Tag) -> None:
        self._append('<sub>')

    def depart_sub(self, node: Tag) -> None:
        self._append('</sub>')

    def visit_sup(self, node: Tag) -> None:
        self._append('<sup>')

    def depart_sup(self, node: Tag) -> None:
        self._append('</sup>')

    def visit_table(self, node: Tag) -> None:
        html_mode = self.opts.tweak_html_tables

        # if we are already in an html table, continue this table as an html
        # formatted table
        if self._is_html_mode():
            html_mode = True

        # if we have more than one table header row, force using html format
        thead_node = node.find('thead', recursive=False)
        if thead_node and len(thead_node.find_all('tr')) > 1:
            html_mode = True

        # if we have a nested table, force html format
        if node.find('table'):
            html_mode = True

        self.html_mode_context.append(html_mode)

        if self._is_html_mode():
            self._append('<table>')
            self._newline()

    def depart_table(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</table>')

        self.html_mode_context.pop()
        self._newline(count=2)

    def visit_tbody(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append(' <tbody>')
            self._newline()

    def depart_tbody(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append(' </tbody>')
            self._newline()

    def visit_td(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<td')

            colspan = node.get('colspan', '')
            if colspan:
                self._append(f' colspan="{colspan}"')

            rowspan = node.get('rowspan', '')
            if rowspan:
                self._append(f' rowspan="{rowspan}"')

            self._append('>')
        else:
            self._append('| ')

            # we will be capturing all output to bind into a single line
            self.output_context.append(self.output)
            self.output = ['']

    def depart_td(self, node: Tag) -> None:
        if self._is_html_mode():
            # strip any trailing whitespaces before closing
            if not self.output[-1].strip():
                self.output.pop()

            self._append('</td>')
        else:
            # group all captured content and restore output capture
            td_contents = ' '.join(''.join(self.output).split())
            self.output = self.output_context.pop()

            self._append(f'{td_contents} ')

            # if this is the last td, close up the row
            next_tag = node.find_next_sibling()
            if not next_tag or next_tag.name != 'td':
                self._append('|\n')

    def visit_th(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<th>')
        else:
            self._append('| ')

            # we will be capturing all output to bind into a single line
            self.output_context.append(self.output)
            self.output = ['']

    def depart_th(self, node: Tag) -> None:
        if self._is_html_mode():
            # strip any trailing whitespaces before closing
            if not self.output[-1].strip():
                self.output.pop()

            self._append('</th>')
        else:
            # group all captured content and restore output capture
            th_contents = ' '.join(''.join(self.output).split())
            self.output = self.output_context.pop()

            self._append(f'{th_contents} ')

            # if this is the last th, close up the row
            next_tag = node.find_next_sibling()
            if not next_tag or next_tag.name != 'th':
                self._append('|\n')

    def visit_thead(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append(' <thead>')
            self._newline()

    def depart_thead(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append(' </thead>')
            self._newline()
        else:
            # after a header, add the line separating from the table's body
            column_count = len(node.find_all('th'))
            if column_count:
                self._append('| - ' * column_count + '|\n')

    def visit_tr(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('  <tr>')
        else:
            # if starting a row and this table never had any header entries,
            # build a dummy/empty header
            assert node.parent
            assert node.parent.parent
            thead_node = node.parent.parent.find('thead')
            if not thead_node and not node.find_previous_sibling():
                column_count = len(node.find_all('td'))
                if column_count:
                    self._append('| ' * column_count + '|\n')
                    self._append('| - ' * column_count + '|\n')

    def depart_tr(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</tr>')
            self._newline()

    def visit_u(self, node: Tag) -> None:
        self._append('<u>')

    def depart_u(self, node: Tag) -> None:
        self._append('</u>')

    def visit_ul(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('<ul>')
        else:
            self.indent_context.append('ul')
            self.indent_offset.append(self.indent_offset[-1] + 2)

    def depart_ul(self, node: Tag) -> None:
        if self._is_html_mode():
            self._append('</ul>')
        else:
            self.indent_context.pop()
            self.indent_offset.pop()
            self._newline()

    def unknown_visit(self, node: Tag) -> None:
        name = self._tag_name(node)
        logger.warning(f'unknown node {name} ({node.name})')

        if self.opts.development:
            logger.error(node)
            raise SystemExit

        raise SkipNode

    def unknown_depart(self, node: Tag) -> None:
        name = self._tag_name(node)

        if self.opts.development:
            logger.error(f'unknown depart {name} ({node.name})')
            logger.error(node)
            raise SystemExit

        logger.debug(f'unknown depart {name} ({node.name})')

    def _is_html_mode(self) -> bool:
        return self.html_mode_context[-1]

    def _resolve_ref(self, target: str) -> str:
        # determine current page's slug and the target's slug in path form
        page_slug_str = self.title2target.get(self.title)
        assert page_slug_str
        page_slug = Path(page_slug_str)
        target_path = Path(target)

        # determine the relative path between the two; we append a `.ext`
        # extension to help the `relative_to` to always treat the target as a
        # file to allow parent-relative paths to be produced if there was no
        # original extension
        ref = target_path.with_name(f'{target_path.name}.ext')
        # ref = ref.relative_to(page_slug.parent, walk_up=True)  py3.12+
        ref = Path(os.path.relpath(ref, page_slug.parent))     # py3.11
        ref = ref.with_name(ref.name.removesuffix('.ext'))

        logger.debug(f'(ref) {page_slug.as_posix()} -> '
                     f'{target_path.as_posix()} : {ref.as_posix()}')

        return ref.as_posix()

    def _newline(self, count: int = 1) -> None:
        for _ in range(count):
            self._append('\n')

    def _append(self, value: str) -> None:
        last_ends_with_nl = self.output[-1].endswith('\n')

        # If starting a new line for an admonition, we will be populating an
        # "> VALUE" for the entry. If the text being processed now is an empty
        # newline, we only want a ">" marking. However, we want to track that
        # this output is pending another admonition line since if we do not
        # eventually add a new line, we will want to pop/drop the setup ">".
        if self.admonition_prefix_context[-1] and last_ends_with_nl:
            self.admonition_prefix_pending = bool(value) and value == '\n'
            if value == '\n':
                self.output.append('>\n')
            else:
                self.output.append(f'> {value}')
        else:
            self.admonition_prefix_pending = False
            self.output.append(value)


class SkipNode(Exception):  # noqa: N818
    pass
