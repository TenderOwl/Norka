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

from gettext import gettext as _

import gi

from norka.gobject_worker import GObjectWorker
from norka.services.export import Exporter

gi.require_version("WebKit2", "4.0")
from gi.repository import WebKit2, Gtk, GObject


class Preview(Gtk.Window):
    __gtype_name__ = 'PreviewWindow'

    # __gsignals__ = {
    #     'print': (GObject.SIGNAL_RUN_FIRST, None, ()),
    # }

    def __init__(self, parent: Gtk.Widget, text: str):
        super().__init__(modal=False)
        self.set_default_size(800, 600)
        self.set_accept_focus(False)

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

        # Render in thread
        self.show_spinner(True)
        GObjectWorker.call(Exporter.render_html, (text,), self.update_html)

        ctx = WebKit2.WebContext.get_default()
        self.web: WebKit2.WebView = WebKit2.WebView.new_with_context(ctx)

        self.add(self.web)

    def buffer_changed(self, buffer: Gtk.TextBuffer):
        self.show_spinner(True)
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        GObjectWorker.call(Exporter.render_html, (text,), self.update_html)

    def update_html(self, html: str):
        self.show_spinner(False)
        self.web.load_html(html)

    def show_spinner(self, state: bool = False) -> None:
        if state:
            self.spinner.start()
        else:
            self.spinner.stop()
        self.spinner.set_visible(state)

    # def scroll_to(self, percent: float):
    #     self.web.run_javascript(f'scrollTo({percent});')
