# rename_popover.py
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

from gi.repository import Gtk, Pango, GObject


class RenamePopover(Gtk.Popover):
    __gtype_name__ = 'RenamePopover'

    __gsignals__ = {
        'activate': (GObject.SignalFlags.ACTION, None, (str,)),
    }

    def __init__(self, relative_to: Gtk.Widget, origin_title: str, label_title: str = None):
        super().__init__()

        self.set_relative_to(relative_to)
        self.set_position(Gtk.PositionType.RIGHT)

        self.origin_title = origin_title

        label = Gtk.Label()
        label.set_markup(label_title or f"<b>{_('Rename')} {self.origin_title}:</b>")
        label.set_halign(Gtk.Align.START)
        label.set_margin_bottom(6)
        label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)

        self.entry = Gtk.Entry(text=self.origin_title)
        self.entry.set_hexpand(True)
        self.entry.connect('changed', self.text_changed)
        self.entry.connect('activate', self.apply_activated)

        grid = Gtk.Grid(margin=12, column_spacing=6, row_spacing=6)
        grid.attach(label, 0, 0, 2, 1)
        grid.attach(self.entry, 0, 1, 1, 1)

        self.rename_button = Gtk.Button(label=_("Rename"))
        self.rename_button.connect('clicked', self.apply_activated)
        self.rename_button.set_sensitive(False)
        self.rename_button.add_css_class("destructive-action")
        grid.attach(self.rename_button, 1, 1, 1, 1)

        self.set_child(grid)

    def text_changed(self, _editable) -> None:
        self.rename_button.set_sensitive(self.origin_title != self.entry.get_text())

    def apply_activated(self, _widget: Gtk.Widget):
        text = self.entry.get_text().strip()
        if self.origin_title != text:
            self.emit('activate', text)
