# search_dialog.py
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

from gi.repository import Gtk, Gdk


class SearchDialog(Gtk.Dialog):
    __gtype_name__ = 'SearchDialog'

    def __init__(self):
        super().__init__(
            deletable=False
        )

        header = Gtk.HeaderBar(title="Search for...")
        header.get_style_context().add_class('search-dialog-header')
        self.set_titlebar(header)

        self.set_default_size(400, 60)
        self.set_modal(True)
        self.set_transient_for(Gtk.Application.get_default().props.active_window)

        revealer = Gtk.Revealer()

        scrolled = Gtk.ScrolledWindow()
        result_box = Gtk.ListBox()
        scrolled.add(result_box)

        # self.get_header_bar().set_visible(False)
        # self.get_header_bar().set_no_show_all(True)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text('Jump to...')

        box = self.get_content_area()
        box.pack_start(self.search_entry, False, True, 0)
        box.pack_end(scrolled, True, True, 0)
        self.set_titlebar(None)

        self.connect('key_release_event', self.on_key_release_event)

        self.show_all()

    def on_key_release_event(self, sender, event_key: Gdk.EventKey):
        if event_key.keyval == Gdk.KEY_Escape:
            self.destroy()

        return False
