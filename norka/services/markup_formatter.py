# markup_formatter.py
#
# MIT License
#
# Copyright (c) 2020 Andrey Maksimov <meamka@ya.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import os
import re
from contextlib import contextmanager

from gi.repository import Gtk

from norka.services.logger import Logger


@contextmanager
def user_action(buffer: Gtk.TextBuffer):
    buffer.begin_user_action()
    yield buffer
    buffer.end_user_action()


class MarkupFormatter:
    def __init__(self, buffer: Gtk.TextBuffer):
        self.buffer = buffer

    def on_insert_italic(self, widget, data=None):
        self.toggle_block(widget, '_')

    def on_insert_bold(self, widget, data=None):
        self.toggle_block(widget, '**')

    def on_insert_strike(self, widget, data=None):
        self.toggle_block(widget, '~~')

    def on_toggle_header1(self, widget, data=None):
        self.toggle_heading(widget, 1)

    def on_toggle_header2(self, widget, data=None):
        self.toggle_heading(widget, 2)

    def on_toggle_header3(self, widget, data=None):
        self.toggle_heading(widget, 3)

    def on_insert_code(self, widget, data=None):
        self.toggle_block(widget, '`')

    def on_insert_code_block(self, widget, data=None):
        self.toggle_block(widget, '```')

    def insert_link(self, widget: Gtk.Widget = None, link: str = None):
        if not link:
            return

        text = link
        if not re.match(r'^http[s]?://', link):
            link = f'https://{link}'

        with user_action(self.buffer):
            if self.buffer.get_has_selection():
                (start, end) = self.buffer.get_selection_bounds()
                text = self.buffer.get_text(start, end, True)
                self.buffer.delete(start, end)
                self.buffer.insert(start, f'[{text}]({link})')
            else:
                self.buffer.insert_at_cursor(f'[{text}]({link})')

    def insert_image_link(self, widget: Gtk.Widget = None, link: str = None):
        if not link:
            return

        text = os.path.basename(link.strip())

        with user_action(self.buffer):
            if self.buffer.get_has_selection():
                (start, end) = self.buffer.get_selection_bounds()
                text = self.buffer.get_text(start, end, True)
                self.buffer.delete(start, end)
                self.buffer.insert(start, f'[{text}]({link})')
            else:
                self.buffer.insert_at_cursor(f'[{text}]({link})')


    def toggle_block(self, text_view: Gtk.TextView, markup: str) -> None:
        """Apply text block markup to currently selected line.
        If selected text placed within markup tags and it matches required markup,
        it removes markup.

        :param text_view: Gtk.TextView widget
        :param markup: tag to apply to selection.
        """
        markup_length = len(markup)

        with user_action(self.buffer):

            # If self.buffer has selected text then work with it
            if self.buffer.get_has_selection():
                (start, end) = self.buffer.get_selection_bounds()

            # If there is no selection but the cursor placed inside a word
            else:
                cursor_mark = self.buffer.get_insert()
                cursor_iter = self.buffer.get_iter_at_mark(cursor_mark)

                start = cursor_iter.copy()
                end = cursor_iter.copy()
                # start.backward_word_start()
                # end.forward_word_end()

            # Get the origin text
            origin = self.buffer.get_text(start, end, True)

            if start.get_offset() >= markup_length and end.get_offset() + markup_length <= self.buffer.get_char_count():
                ext_start = start.copy()
                ext_start.backward_chars(markup_length)
                ext_end = end.copy()
                ext_end.forward_chars(markup_length)

                # Check for markup on the sides of the selection
                ext_text = self.buffer.get_text(ext_start, ext_end, True)
                if ext_text.startswith(markup) and ext_text.endswith(markup):
                    text = ext_text[markup_length:-markup_length]
                    self.buffer.delete(ext_start, ext_end)
                    move_back = 0
                else:
                    self.buffer.delete(start, end)
                    text = markup + origin + markup
                    move_back = markup_length
            else:
                self.buffer.delete(start, end)
                text = markup + origin + markup
                move_back = markup_length

            self.buffer.insert_at_cursor(text)

            cursor_mark = self.buffer.get_insert()
            cursor_iter = self.buffer.get_iter_at_mark(cursor_mark)
            cursor_iter.backward_chars(move_back)
            self.buffer.move_mark_by_name('selection_bound', cursor_iter)
            cursor_iter.backward_chars(len(origin))
            self.buffer.move_mark_by_name('insert', cursor_iter)

    def toggle_heading(self, text_view: Gtk.TextView, size: int) -> None:
        """Apply heading markup to currently selected line.
        If line starts with markup, and it matches required header size,
        it removes it.

        :param text_view: Gtk.TextView widget
        :param size: header size from 1 to 6
        """
        with user_action(self.buffer):
            cursor_mark = self.buffer.get_insert()
            cursor_iter = self.buffer.get_iter_at_mark(cursor_mark)
            offset = cursor_iter.get_offset()

            start = cursor_iter.copy()
            end = cursor_iter.copy()
            start.backward_chars(start.get_line_offset())
            end.forward_to_line_end()

            # Get the origin text
            origin: str = self.buffer.get_text(start, end, True)
            markup = (size * '#') + ' '

            Logger.info(f'origin: {origin}')

            pattern = re.compile(r'^(#{1,6})\s')
            match = pattern.match(origin)

            # If pattern found
            if match and match.group(1):
                # if line already header of `size`
                if len(match.group(1)) == size:
                    text = pattern.sub('', origin)
                else:
                    text = markup + origin
            else:
                text = markup + origin

            self.buffer.delete(start, end)

            self.buffer.insert(start, text)

    def toggle_line(self, text_view: Gtk.TextView, markup: str) -> None:
        """Apply heading markup to currently selected line.
        If line starts with markup and it matches required header size,
        it removes it.

        :param text_view: Gtk.TextView widget
        :param markup: header size from 1 to 6
        """
        markup += ' '

        with user_action(self.buffer):

            if self.buffer.get_has_selection():
                (start, end) = self.buffer.get_selection_bounds()
            else:
                cursor_mark = self.buffer.get_insert()
                cursor_iter = self.buffer.get_iter_at_mark(cursor_mark)

                start = cursor_iter.copy()
                end = cursor_iter.copy()

            start.backward_chars(start.get_line_offset())
            end.forward_to_line_end()

            text = self.buffer.get_text(start, end, True)
            lines = text.splitlines()

            has_markup = all(line.startswith(markup) for line in lines)

            new_lines = []
            for line in lines:
                if has_markup:
                    new_lines.append(line[len(markup):])
                else:
                    new_lines.append(markup + line)

            self.buffer.delete(start, end)
            self.buffer.insert_at_cursor('\n'.join(new_lines))

    def toggle_ordered_list(self, text_view: Gtk.TextView) -> None:
        with user_action(self.buffer):

            if self.buffer.get_has_selection():
                (start, end) = self.buffer.get_selection_bounds()
            else:
                cursor_mark = self.buffer.get_insert()
                cursor_iter = self.buffer.get_iter_at_mark(cursor_mark)

                start = cursor_iter.copy()
                end = cursor_iter.copy()

            start.backward_chars(start.get_line_offset())
            end.forward_to_line_end()

            text = self.buffer.get_text(start, end, True)
            lines = text.splitlines()

            pattern = re.compile(r'^[0-9]+\.')

            has_markup = all(pattern.match(line) for line in lines)

            new_lines = []
            for index, line in enumerate(lines, 1):
                if has_markup:
                    sub = line.find('. ') + 2
                    new_lines.append(line[sub:])
                else:
                    new_lines.append(f'{index}. {line}')

            self.buffer.delete(start, end)
            self.buffer.insert_at_cursor('\n'.join(new_lines))
