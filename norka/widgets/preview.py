# preview.py
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
import tempfile
from gettext import gettext as _

import gi

from norka.gobject_worker import GObjectWorker
from norka.services.export import Exporter

gi.require_version("WebKit2", "4.0")
from gi.repository import WebKit2, Gtk, Granite


class Preview(Gtk.Window):
    __gtype_name__ = 'PreviewWindow'

    # __gsignals__ = {
    #     'print': (GObject.SIGNAL_RUN_FIRST, None, ()),
    # }

    def __init__(self, parent: Gtk.Widget, text: str = None):
        super().__init__(modal=False)
        self.set_default_size(800, 600)
        self.set_transient_for(parent)

        # print_button = Gtk.Button.new_from_icon_name('document-print', Gtk.IconSize.LARGE_TOOLBAR)
        # print_button.set_tooltip_markup(Granite.markup_accel_tooltip(None, _('Print document')))
        # print_button.connect('clicked', lambda x: self.emit('print'))

        self.spinner = Gtk.Spinner(visible=False)

        header = Gtk.HeaderBar(title=_("Preview"))
        header.set_has_subtitle(False)
        header.set_show_close_button(True)
        header.get_style_context().add_class('norka-header')

        header.pack_start(self.spinner)
        # header.pack_end(print_button)

        self.set_titlebar(header)

        self.temp_file = tempfile.NamedTemporaryFile(prefix='norka-', delete=False)

        # Render in thread
        if text:
            GObjectWorker.call(Exporter.export_html_preview, (self.temp_file.name, text,), self.update_html)

        ctx = WebKit2.WebContext.get_default()
        self.web: WebKit2.WebView = WebKit2.WebView.new_with_context(ctx)
        self.web.connect('load-changed', self.on_load_changed)
        web_settings = self.web.get_settings()
        web_settings.set_enable_developer_extras(False)
        web_settings.set_enable_tabs_to_links(False)
        self.web.set_settings(web_settings)

        self.empty = Granite.WidgetsWelcome()
        self.empty.set_title(_('Nothing to preview'))
        self.empty.set_subtitle(_('To render preview open a document'))

        self.stack = Gtk.Stack()
        self.stack.add_named(self.empty, 'empty-page')
        self.stack.add_named(self.web, 'preview-page')

        self.add(self.stack)

    def buffer_changed(self, buffer: Gtk.TextBuffer):
        self.show_spinner(True)
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        GObjectWorker.call(Exporter.export_html_preview, (self.temp_file.name, text,), self.update_html)

    def on_load_changed(self, webview: WebKit2.WebView, event: WebKit2.LoadEvent):
        if event.STARTED:
            self.show_spinner(True)
        if event.FINISHED:
            self.show_spinner(False)

    def update_html(self, html: str):
        self.web.load_uri('file://' + html)

    def show_spinner(self, state: bool = False) -> None:
        if state:
            self.spinner.start()
        else:
            self.spinner.stop()
        self.spinner.set_visible(state)

    def show_preview(self, sender=None, event=None):
        self.stack.set_visible_child_name('preview-page')

    def show_empty_page(self, sender=None, event=None):
        self.stack.set_visible_child_name('empty-page')

    def scroll_to(self, percent: float):
        self.web.run_javascript(f'scrollTo({percent});', None, print)
