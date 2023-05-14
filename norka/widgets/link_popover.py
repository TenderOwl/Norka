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


class LinkPopover(Gtk.Popover):
    __gtype_name__ = 'LinkPopover'

    __gsignals__ = {
        'insert-link': (GObject.SignalFlags.ACTION, None, (str,)),
    }

    def __init__(self, relative_to: Gtk.Widget):
        super().__init__()
        self.set_relative_to(relative_to)
        self.set_position(Gtk.PositionType.BOTTOM)

        link_label = Gtk.Label(_('Link to insert:'), halign=Gtk.Align.START, hexpand=True)

        self.link_entry = Gtk.Entry(placeholder_text=_('https://tenderowl.com'))
        self.link_entry.connect('activate', self.on_activate)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      spacing=6,
                      width_request=200,
                      margin_bottom=12,
                      margin_top=12,
                      margin_end=12,
                      margin_start=12, )
        box.append(link_label)
        box.append(self.link_entry)

        self.set_child(box)

    def set_link(self, link: str = None):
        self.link_entry.set_text(link or '')

    def on_activate(self, entry: Gtk.Entry):
        self.emit('insert-link', entry.get_text().strip())
