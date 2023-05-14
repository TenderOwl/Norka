# folder_create_dialog.py
#
# MIT License
#
# Copyright (c) 2020-2022 Andrey Maksimov <meamka@ya.ru>
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

from gi.repository import Gtk, Adw


class FolderCreateDialog(Adw.Window):
    __gtype_name__ = 'FolderCreateDialog'

    def __init__(self, folder_title=None):
        super().__init__(title=_("Create folder"))

        self.set_default_size(300, 100)
        self.set_modal(True)
        self.set_transient_for(Gtk.Application.get_default().props.active_window)

        header = Gtk.Label(label=_('Create folder'), css_classes=['title-1'], halign=Gtk.Align.CENTER)

        self.entry = Gtk.Entry(placeholder_text=_('Folder name'), hexpand=True)
        self.entry.set_text(folder_title)
        self.entry.connect('activate', lambda entry: self.response(Gtk.ResponseType.ACCEPT))

        layout = Gtk.Grid(row_spacing=12, margin_start=12, margin_end=12)
        layout.attach(header, 0, 0, 1, 1)
        layout.attach(self.entry, 0, 1, 1, 1)

        self.set_content(layout)
        # self.add_button(_("Cancel"), Gtk.ResponseType.CANCEL)

        # suggested_button = self.add_button(_("Create"), Gtk.ResponseType.ACCEPT)
        # suggested_button.get_style_context().add_class(Gtk.STYLE_CLASS_SUGGESTED_ACTION)

    @property
    def folder_title(self):
        return self.entry.get_text().strip()
