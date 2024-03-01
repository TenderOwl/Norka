# welcome.py
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
import os
from gettext import gettext as _
from urllib.parse import urlparse, unquote_plus

from gi.repository import Gtk, Gdk, GObject, Adw

from norka.define import TARGET_ENTRY_TEXT


class Welcome(Adw.Bin):
    __gtype_name__ = 'NorkaWelcome'

    __gsignals__ = {
        'document-import': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__()

        container = Adw.StatusPage()
        container.set_title(_('No documents yet'))
        container.set_description(_('Create or import and start writing'))
        container.set_icon_name('com.github.tenderowl.norka')

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        create_btn = Gtk.Button(label=_('New document'), action_name='document.create',
                                tooltip_text=_('Create empty document'))
        create_btn.set_icon_name('document-new-symbolic')
        box.append(create_btn)

        import_btn = Gtk.Button(label=_('Import document'), action_name='document.import',
                                tooltip_text=_('Import document'))
        import_btn.set_icon_name('folder-open-symbolic')
        box.append(import_btn)

        container.set_child(box)

        self.set_child(container)

        # Enable drag-drop
        # enforce_target = Gtk.TargetEntry.new('text/plain', Gtk.TargetFlags.OTHER_APP, TARGET_ENTRY_TEXT)
        # self.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP | Gtk.DestDefaults.HIGHLIGHT,
        #                    [enforce_target], Gdk.DragAction.COPY)
        # self.connect('drag-data-received', self.on_drag_data_received)

    # def on_drag_data_received(self, widget: Gtk.Widget, drag_context: Gdk.DragContext, x: int, y: int,
    #                           data: Gtk.SelectionData, info: int, time: int) -> None:
    #     if info == TARGET_ENTRY_TEXT:
    #         uris = data.get_text().split('\n')
    #
    #         for uri in uris:
    #             # Skip empty items
    #             if not uri:
    #                 continue
    #
    #             p = urlparse(unquote_plus(uri))
    #             filename = os.path.abspath(os.path.join(p.netloc, p.path))
    #
    #             self.emit('document-import', filename)
