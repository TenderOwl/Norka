# rename_dialog.py
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
from gi.repository import Gtk, Pango

from norka.define import APP_TITLE


class RenameDialog(Gtk.Dialog):
    __gtype_name__ = 'RenameDialog'

    def __init__(self, origin_title):
        super().__init__()

        self.set_default_size(240, 100)
        self.set_modal(True)
        self.set_transient_for(Gtk.Application.get_default().props.active_window)
        self.set_title(APP_TITLE)
        self.add_button(_('Cancel'), Gtk.ResponseType.CANCEL)

        self.origin_title = origin_title

        label = Gtk.Label()
        label.set_markup(_('<b>Rename {} to:</b>').format(self.origin_title))
        label.set_halign(Gtk.Align.START)
        label.set_margin_bottom(6)
        label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        self.entry = Gtk.Entry(text=self.origin_title)
        self.entry.set_hexpand(True)
        self.entry.connect('changed', self.text_changed)
        self.entry.connect('activate', self.apply_activated)

        grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=6)
        grid.add(label)
        grid.add(self.entry)

        self.rename_button = Gtk.Button(label=_("Rename"))
        self.rename_button.set_sensitive(False)
        self.rename_button.get_style_context().add_class("destructive-action")
        self.add_action_widget(self.rename_button, Gtk.ResponseType.APPLY)

        box = self.get_content_area()
        box.add(grid)
        self.show_all()

    def text_changed(self, editable) -> None:
        self.rename_button.set_sensitive(self.origin_title != self.entry.get_text())

    def apply_activated(self, entry: Gtk.Entry):
        if self.origin_title != self.entry.get_text():
            self.response(Gtk.ResponseType.APPLY)
