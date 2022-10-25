# editor_view.py
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


import re

import gi

from norka.models.document import Document
from norka.services.logger import Logger
from norka.services.markup_formatter import MarkupFormatter
from norka.services.stats_handler import StatsHandler
from norka.services.storage import storage
from norka.widgets.editor import Editor
from norka.widgets.search_bar import SearchBar

from gi.repository import Gtk, GtkSource, Gdk, GtkSpell, Pango, Granite, GObject


class EditorView(Gtk.Grid):
    __gtype_name__ = 'EditorView'

    def __init__(self):
        super().__init__()

        self.document = None

        self.view = Editor()

        self.scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        self.scrolled.get_style_context().add_class('scrolled-editor')
        self.scrolled.add(self.view)

        # SearchBar
        self.search_bar = SearchBar()
        self.search_revealer = Gtk.Revealer()
        self.search_revealer.add(self.search_bar)
        self.search_bar.connect('find-changed', self.do_next_match)
        self.search_bar.connect('find-next', self.do_next_match)
        self.search_bar.connect('find-prev', self.do_previous_match)
        self.search_bar.connect('stop-search', self.do_stop_search)

        content_grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        content_grid.pack_start(self.search_revealer, False, True, 0)
        content_grid.pack_start(self.scrolled, True, True, 0)
        content_grid.show_all()

        self.overlay = Gtk.Overlay()
        self.overlay.add(content_grid)
        self.stats_overlay = Granite.WidgetsOverlayBar.new(self.overlay)

        self.stats_handler = StatsHandler(overlay_bar=self.stats_overlay, buffer=self.buffer)
        self.stats_handler.update_default_stat()

        self.add(self.overlay)

        self.font_desc = Pango.FontDescription()
        self.spellchecker = GtkSpell.Checker()

        self.search_settings = GtkSource.SearchSettings(wrap_around=True)
        self.search_context = GtkSource.SearchContext(buffer=self.buffer, settings=self.search_settings)
        self.search_iter = None

    def create_document(self, title: str = 'Nameless') -> None:
        """Create new document and put it to storage

        :param title: title of the document. Defaults to 'Nameless'
        :type title: str
        :return: None
        """
        self.document = Document(title=title)
        self.document.document_id = storage.add(self.document)
        self.view.grab_focus()

    def load_document(self, doc_id: int) -> None:
        """Load :model:`Document` from storage with given `doc_id`.

        :param doc_id: id of the document to load
        :type doc_id: int
        :return: None
        """
        self.document = storage.get(doc_id)

        self.buffer.set_text(self.document.content)
        self.buffer.end_not_undoable_action()
        self.buffer.set_modified(False)
        self.buffer.place_cursor(self.buffer.get_start_iter())
        self.view.grab_focus()

    def unload_document(self, save=True) -> None:
        """Save current document and clear text buffer

        :return: None
        """
        # self.stats_overlay.destroy()
        if not self.document:
            return

        if save:
            self.save_document()
        self.buffer.set_text('')
        self.document = None
        self.hide_search_bar()

    def hide_search_bar(self):
        self.search_revealer.set_reveal_child(False)
        self.search_bar.stop_search()

    def load_file(self, path: str) -> bool:
        self.buffer.begin_not_undoable_action()
        try:
            txt = open(path).read()
        except Exception as e:
            Logger.error(e)
            return False

        self.buffer.set_text(txt)
        self.buffer.end_not_undoable_action()
        self.buffer.set_modified(False)
        self.buffer.place_cursor(self.buffer.get_start_iter())

        return True

    def save_document(self) -> bool:
        if not self.document:
            return False

        text = self.buffer.get_text(
            self.buffer.get_start_iter(),
            self.buffer.get_end_iter(),
            True
        )
        if self.document.title in ('', 'Nameless'):
            try:
                self.document.title = text.partition('\n')[0].lstrip(' #') or "Nameless"
            except TypeError:
                pass

        if storage.update(self.document.document_id, {"content": text, 'title': self.document.title}):
            self.document.content = text
            Logger.debug('Document %s saved', self.document.document_id)
            return True

    def get_text(self) -> str:
        return self.buffer.get_text(
            self.buffer.get_start_iter(),
            self.buffer.get_end_iter(),
            True
        ).strip()

    def on_key_release_event(self, text_view: GtkSource.View, event: Gdk.EventKey) -> None:
        """Handle release event and iterate markdown list markup

        :param text_view: widget emitted the event
        :param event: key release event
        :return:
        """
        buffer = text_view.get_buffer()
        if event.keyval == Gdk.KEY_Return:
            buffer.begin_user_action()
            curr_iter = buffer.get_iter_at_mark(buffer.get_insert())
            curr_line = curr_iter.get_line()
            if curr_line > 0:
                # Get prev line text
                prev_line = curr_line - 1
                prev_iter = buffer.get_iter_at_line(prev_line)
                prev_line_text = buffer.get_text(prev_iter, curr_iter, False)
                # Check if prev line starts from markdown list chars
                match = re.search(r"^(\s){,4}([0-9]*.|-|\*|\+)\s+", prev_line_text)
                if match:
                    sign = match.group(2)
                    if re.match(r'^[0-9]+.', sign):
                        # ordered list should increment number
                        sign = str(int(sign[:-1]) + 1) + '.'

                    buffer.insert_at_cursor(sign + ' ')

            buffer.end_user_action()

    def on_search_text_activated(self, sender: Gtk.Widget = None, event=None):
        state = self.search_revealer.get_child_revealed()
        if not state:
            # If there is selected text in view put it as search text
            bounds = self.buffer.get_selection_bounds()
            if bounds:
                text = bounds[0].get_text(bounds[1])
                self.search_bar.search_entry.set_text(text)

            self.search_revealer.set_reveal_child(True)
            self.search_bar.search_entry.grab_focus()

    def set_spellcheck(self, spellcheck: bool) -> None:
        if spellcheck:
            self.spellchecker.attach(self.view)
        else:
            self.spellchecker.detach()

    def set_style_scheme(self, scheme_id: str) -> None:
        scheme = GtkSource.StyleSchemeManager().get_scheme(scheme_id)
        self.buffer.set_style_scheme(scheme)

        try:
            bgcolor = scheme.get_style('text').props.background
        except AttributeError:
            bgcolor = '#fff'

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(f'.scrolled-editor {{background: {bgcolor}}}'.encode('ascii'))
        self.scrolled.get_style_context().add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def update_font(self, font: str) -> None:
        self.font_desc = Pango.FontDescription.from_string(font)
        self.view.override_font(self.font_desc)

    def do_stop_search(self, event: Gdk.Event = None) -> None:
        self.search_revealer.set_reveal_child(False)
        self.view.grab_focus()

    def search(self, text: str, forward: bool = True) -> bool:

        self.search_context.set_highlight(False)

        # Can't search anything in an inexistent buffer and/or without anything to search.
        if any([not self.buffer, not self.get_text(), not text]):
            self.search_bar.search_entry.props.primary_icon_name = "edit-find-symbolic"
            return False

        self.search_context.set_highlight(True)

        if self.search_settings.get_search_text() != text:
            self.search_settings.set_search_text(text)
            self.search_iter = self.buffer.get_iter_at_mark(self.buffer.get_insert())
        elif self.search_iter:
            self.search_iter.forward_char()
        else:
            return False

        if forward:
            found, self.search_iter = self.search_for_iter(self.search_iter)
        else:
            found, self.search_iter = self.search_for_iter_backward(self.search_iter)

        if found:
            self.search_bar.search_entry.get_style_context().remove_class(Gtk.STYLE_CLASS_ERROR)
            self.search_bar.search_entry.props.primary_icon_name = "edit-find-symbolic"
        else:
            self.search_iter = self.buffer.get_start_iter()
            found, end_iter = self.search_for_iter(self.search_iter)
            if found:
                self.search_bar.search_entry.get_style_context().remove_class(Gtk.STYLE_CLASS_ERROR)
                self.search_bar.search_entry.props.primary_icon_name = "edit-find-symbolic"
            else:
                self.search_iter.set_offset(-1)
                self.buffer.select_range(self.search_iter, self.search_iter)
                self.search_bar.search_entry.get_style_context().add_class(Gtk.STYLE_CLASS_ERROR)
                self.search_bar.search_entry.props.primary_icon_name = "dialog-error-symbolic"
                return False

        return True

    def search_for_iter(self, start_iter) -> (bool, Gtk.TextIter):
        found, start_iter, end_iter, has_wrapped = self.search_context.forward2(start_iter)
        if found:
            self.scroll_to(start_iter, end_iter)
        return found, end_iter

    def search_for_iter_backward(self, start_iter) -> (bool, Gtk.TextIter):
        found, start_iter, end_iter, has_wrapped = self.search_context.backward2(start_iter)
        if found:
            self.scroll_to(start_iter, end_iter)
        return found, start_iter

    def do_next_match(self, sender, text: str) -> bool:
        return self.search(text)

    def do_previous_match(self, sender, text: str) -> bool:
        return self.search(text, False)

    def search_forward(self, sender=None, event=None) -> bool:
        return self.do_next_match(sender, self.search_bar.search_entry.get_text())

    def search_backward(self, sender=None, event=None) -> bool:
        return self.do_previous_match(sender, self.search_bar.search_entry.get_text())

    def scroll_to(self, start_iter, end_iter):

        mark = self.buffer.create_mark(None, start_iter, False)
        self.view.scroll_to_mark(mark, 0, False, 0, 0)

        self.buffer.place_cursor(start_iter)
        self.buffer.select_range(start_iter, end_iter)

