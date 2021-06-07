# editor.py
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
from typing import Tuple

import gi
from gi.repository import Gtk, GtkSource, Gdk, GtkSpell, Pango, Granite, GObject

from norka.models.document import Document
from norka.services.logger import Logger
from norka.services.markup_formatter import MarkupFormatter
from norka.services.stats_handler import StatsHandler
from norka.services.storage import Storage
from norka.widgets.image_link_popover import ImageLinkPopover
from norka.widgets.link_popover import LinkPopover
from norka.widgets.search_bar import SearchBar


class Editor(Gtk.Grid):
    __gtype_name__ = 'Editor'

    __gsignals__ = {
        'document-load': (GObject.SignalFlags.ACTION, None, (int,)),
        'document-close': (GObject.SignalFlags.ACTION, None, (int,)),
        'insert-italic': (GObject.SignalFlags.ACTION, None, ()),
        'insert-bold': (GObject.SignalFlags.ACTION, None, ()),
        'insert-code': (GObject.SignalFlags.ACTION, None, ()),
        'insert-code-block': (GObject.SignalFlags.ACTION, None, ()),
        'insert-h1': (GObject.SignalFlags.ACTION, None, ()),
        'insert-h2': (GObject.SignalFlags.ACTION, None, ()),
        'insert-h3': (GObject.SignalFlags.ACTION, None, ()),
        'insert-list': (GObject.SignalFlags.ACTION, None, ()),
        'insert-ordered-list': (GObject.SignalFlags.ACTION, None, ()),
        'insert-quote': (GObject.SignalFlags.ACTION, None, ()),
        'insert-link': (GObject.SignalFlags.ACTION, None, ()),
        'insert-image': (GObject.SignalFlags.ACTION, None, ()),
    }

    def __init__(self, storage: Storage):
        super().__init__()

        self.document = None
        self.storage = storage

        self.buffer = GtkSource.Buffer()
        self.manager = GtkSource.LanguageManager()
        self.language = self.manager.get_language("markdown")
        self.buffer.set_language(self.language)
        self.buffer.create_tag('match', background="#66ff00")

        self.view = GtkSource.View()
        self.view.set_buffer(self.buffer)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.view.set_auto_indent(True)
        self.view.set_smart_home_end(True)
        self.view.set_insert_spaces_instead_of_tabs(True)
        self.view.set_tab_width(4)
        self.view.props.width_request = 800
        self.view.set_halign(Gtk.Align.CENTER)

        # self.view.set_pixels_above_lines(2)
        # self.view.set_pixels_below_lines(2)
        # self.view.set_pixels_inside_wrap(4)
        self.view.set_top_margin(8)
        self.view.set_left_margin(8)
        self.view.set_right_margin(8)
        self.view.set_bottom_margin(8)
        self.view.set_monospace(True)
        self.view.get_style_context().add_class('norka-editor')

        self.view.connect('key-release-event', self.on_key_release_event)

        # Connect markup handler
        self.markup_formatter = MarkupFormatter(self.buffer)

        self.get_style_context().add_class('norka-editor-view')
        self.connect('insert-bold', self.on_insert_bold)
        self.connect('insert-italic', self.on_insert_italic)
        self.connect('insert-code', self.on_insert_code)
        self.connect('insert-code-block', self.on_insert_code_block)
        self.connect('insert-h1', self.on_toggle_header1)
        self.connect('insert-h2', self.on_toggle_header2)
        self.connect('insert-h3', self.on_toggle_header3)
        self.connect('insert-list', self.on_toggle_list)
        self.connect('insert-ordered-list', self.on_toggle_ordered_list)
        self.connect('insert-quote', self.on_toggle_quote)
        self.connect('insert-link', self.on_insert_link)
        self.connect('insert-image', self.on_insert_image)

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
        self.search_context = GtkSource.SearchContext(buffer=self.buffer,
                                                      settings=self.search_settings)
        self.search_iter = None

    def create_document(self, title: str = 'Nameless') -> None:
        """Create new document and put it to storage

        :param title: title of the document. Defaults to 'Nameless'
        :type title: str
        :return: None
        """
        self.document = Document(title=title)
        self.view.grab_focus()
        self.emit('document-load', self.document.document_id)

    def load_document(self, doc_id: int) -> None:
        """Load :model:`Document` from storage with given `doc_id`.

        :param doc_id: id of the document to load
        :type doc_id: int
        :return: None
        """
        self.document = self.storage.get(doc_id)

        self.buffer.set_text(self.document.content)
        self.buffer.end_not_undoable_action()
        self.buffer.set_modified(False)
        self.buffer.place_cursor(self.buffer.get_start_iter())
        self.view.grab_focus()
        self.emit('document-load', self.document.document_id)

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
        self.emit('document-close', self.document.document_id)
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
        ).strip()

        # New document has id == -1
        # No need to save new empty documents
        if self.document.document_id == -1 and len(text) == 0:
            # storage.delete(self.document.document_id)
            return False

        if self.document.title in ('', 'Nameless'):
            try:
                self.document.title = text.partition('\n')[0].lstrip(' #') or "Nameless"
            except TypeError:
                pass

        # Save new document to get ID before continue
        if self.document.document_id == -1:
            self.document.document_id = self.storage.add(self.document)

        if self.storage.update(self.document.document_id,
                               {"content": text, 'title': self.document.title}):
            self.document.content = text
            Logger.debug('Document %s saved', self.document.document_id)
            return True

    def get_text(self) -> str:
        return self.buffer.get_text(
            self.buffer.get_start_iter(),
            self.buffer.get_end_iter(),
            True
        ).strip()

    def get_selected_text(self) -> str:
        buffer = self.view.get_buffer()

        if buffer.get_has_selection():
            (start, end) = buffer.get_selection_bounds()
            return buffer.get_text(start, end, True)

    def on_key_release_event(self, text_view: GtkSource.View, event: Gdk.EventKey) -> None:
        """Handle release event and iterate markdown list markup

        :param text_view: widget emitted the event
        :param event: key release event
        :return:
        """
        buffer = text_view.get_buffer()
        if event.keyval == Gdk.KEY_Return and event.get_state() != Gdk.ModifierType.SHIFT_MASK:
            buffer.begin_user_action()
            curr_iter = buffer.get_iter_at_mark(buffer.get_insert())
            curr_line = curr_iter.get_line()
            if curr_line > 0:
                # Get prev line text
                prev_line = curr_line - 1
                prev_iter = buffer.get_iter_at_line(prev_line)
                prev_line_text = buffer.get_text(prev_iter, curr_iter, False)
                # Check if prev line starts from markdown list chars
                match = re.search(r"^(\s){,4}([0-9]\.|-|\*|\+)\s+", prev_line_text)
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
        self.scrolled.get_style_context().add_provider(css_provider,
                                                       Gtk.STYLE_PROVIDER_PRIORITY_USER)

    def update_font(self, font: str) -> None:
        self.font_desc = Pango.FontDescription.from_string(font)
        self.view.override_font(self.font_desc)

    def do_stop_search(self, event: Gdk.Event = None) -> None:
        self.search_revealer.set_reveal_child(False)
        self.view.grab_focus()

    def search(self, text: str, forward: bool = True) -> bool:

        self.search_context.set_highlight(False)

        # Can't search anything in an inexistant buffer and/or without anything to search.
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

    def search_for_iter(self, start_iter) -> Tuple[bool, Gtk.TextIter]:
        found, start_iter, end_iter, has_wrapped = self.search_context.forward2(start_iter)
        if found:
            self.scroll_to(start_iter, end_iter)
        return found, end_iter

    def search_for_iter_backward(self, start_iter) -> Tuple[bool, Gtk.TextIter]:
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

    def get_cursor_coods(self) -> Gdk.Rectangle:

        buffer = self.view.get_buffer()
        mark = buffer.get_insert()
        cursor_iter = buffer.get_iter_at_mark(mark)
        cursor_location = self.view.get_iter_location(cursor_iter)

        buffer_x, buffer_y = self.view.buffer_to_window_coords(
            Gtk.TextWindowType.WIDGET,
            cursor_location.x,
            cursor_location.y
        )

        window = self.view.get_window(Gtk.TextWindowType.WIDGET)
        win_x, win_y = window.get_position()

        offset = (self.scrolled.get_clip().width - self.view.get_clip().width) / 2

        xx = buffer_x + win_x - offset
        yy = buffer_y + win_y + cursor_location.height

        rect = Gdk.Rectangle()
        rect.x = xx
        rect.y = yy
        return rect

    def on_insert_italic(self, widget, data=None):
        self.markup_formatter.toggle_block(self.view, '_')

    def on_insert_bold(self, widget, data=None):
        self.markup_formatter.toggle_block(self.view, '**')

    def on_insert_strike(self, widget, data=None):
        self.markup_formatter.toggle_block(self.view, '~~')

    def on_insert_code(self, widget, data=None):
        self.markup_formatter.toggle_block(self.view, '`')

    def on_insert_code_block(self, widget, data=None):
        self.markup_formatter.toggle_block(self.view, '```')

    def on_toggle_header1(self, widget, data=None):
        self.markup_formatter.toggle_heading(self.view, 1)

    def on_toggle_header2(self, widget, data=None):
        self.markup_formatter.toggle_heading(self.view, 2)

    def on_toggle_header3(self, widget, data=None):
        self.markup_formatter.toggle_heading(self.view, 3)

    def on_toggle_ordered_list(self, widget, data=None):
        self.markup_formatter.toggle_ordered_list(self.view)

    def on_toggle_list(self, widget, data=None):
        self.markup_formatter.toggle_line(self.view, '-')

    def on_toggle_quote(self, widget, data=None):
        self.markup_formatter.toggle_line(self.view, '>')

    def on_insert_link(self, widget, data=None):
        rect = self.get_cursor_coods()
        popover = LinkPopover(self.view)
        popover.set_pointing_to(rect)
        popover.set_link(self.get_selected_text())
        popover.connect('insert-link', self.markup_formatter.insert_link)

        popover.popup()

    def on_insert_image(self, widget, data=None):
        rect = self.get_cursor_coods()
        popover = ImageLinkPopover(self.view)
        popover.set_pointing_to(rect)
        popover.set_link(self.get_selected_text())
        popover.connect('insert-link', self.markup_formatter.insert_image_link)

        popover.popup()
