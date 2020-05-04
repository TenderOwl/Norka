# rename_popover.py
#
# Copyright 2020 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# election-box-aluse or other dealings in this Software without prior written
# authorization.

import os
from gi.repository import Gtk, GObject, Gdk


class RenamePopover(Gtk.Popover):
    __gtype_name__ = 'RenamePopover'

    def __init__(self, relative_to, origin_title):
        super().__init__()

        self.origin_title = origin_title

        self.set_relative_to(relative_to)
        self.set_position(Gtk.PositionType.RIGHT)

        label = Gtk.Label()
        label.set_markup('<b>Rename to</b>')

        self.entry = Gtk.Entry()
        self.entry.set_hexpand(True)
        self.entry.connect('changed', self.text_changed)

        self.rename_button = Gtk.Button(label="Rename")
        self.rename_button.set_margin_start(6)
        self.rename_button.set_sensitive(False)
        self.rename_button.get_style_context().add_class("destructive-action")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, margin=6)
        box.set_hexpand(True)
        box.pack_start(self.entry, True, True, 0)
        box.pack_end(self.rename_button, False, True, 0)

        grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, margin=12)
        grid.add(label)
        grid.add(box)

        self.add(grid)

    def text_changed(self, editable) -> None:
        self.rename_button.set_sensitive(self.orrigin_title != self.entry.get_text())
