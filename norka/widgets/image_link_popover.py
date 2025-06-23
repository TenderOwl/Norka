# link_popover.py
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

from gi.repository import Gtk, GObject


class ImageLinkPopover(Gtk.Popover):
    __gtype_name__ = 'ImageLinkPopover'

    __gsignals__ = {
        'insert-link': (GObject.SignalFlags.ACTION, None, (str,)),
    }

    def __init__(self, relative_to: Gtk.Widget):
        super().__init__()
        self.set_relative_to(relative_to)
        self.set_position(Gtk.PositionType.BOTTOM)

        link_label = Gtk.Label(_('Image link to insert:'), halign=Gtk.Align.START, hexpand=True)

        self.link_entry = Gtk.Entry(placeholder_text=_('https://tenderowl.com'))
        self.link_entry.connect('activate', self.on_activate)

        select_button = Gtk.Button(_('Choose'))
        select_button.connect('clicked', self.on_select_clicked)

        box = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL,
                       column_spacing=6,
                       row_spacing=6,
                       width_request=200,
                       margin_bottom=12,
                       margin_top=12,
                       margin_right=12,
                       margin_left=12, )
        box.attach(link_label, 0, 0, 2, 1)
        box.attach(self.link_entry, 0, 1, 1, 1)
        box.attach(select_button, 1, 1, 1, 1)

        self.set_child(box)
        self.link_entry.grab_focus_without_selecting()

        select_button.grab_remove()
        self.link_entry.grab_focus_without_selecting()

    def set_link(self, link: str = None):
        self.link_entry.set_text(link or '')

    def on_activate(self, entry: Gtk.Entry):
        self.emit('insert-link', entry.get_text().strip())

    def on_select_clicked(self, widget: Gtk.Widget):
        dialog = Gtk.FileChooserNative.new(
            _("Select image to insert"),
            Gtk.Application.get_default().get_active_window(),
            Gtk.FileChooserAction.OPEN
        )

        filter_markdown = Gtk.FileFilter()
        filter_markdown.set_name(_("Images"))
        filter_markdown.add_mime_type("image/*")
        dialog.add_filter(filter_markdown)
        dialog_result = dialog.run()

        if dialog_result == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_filename()
            self.emit('insert-link', file_path)

        dialog.destroy()
