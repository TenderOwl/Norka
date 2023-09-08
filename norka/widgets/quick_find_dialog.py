# quick_find_dialog.py
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

from gi.repository import Gtk, Gio, GObject, Adw, Pango

from norka.models.document import Document
from norka.services.storage import Storage


class QuickFindDialog(Adw.Window):
    __gtype_name__ = 'QuickFindDialog'

    __gsignals__ = {
        'document-activated': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    def __init__(self, storage: Storage):
        super().__init__(title=_("Quick Find"), modal=True,
                         transient_for=Gtk.Application.get_default().props.active_window,
                         width_request=400, height_request=200,
                         default_width=400, default_height=200)

        self.add_css_class("quick-find-dialog")

        self.storage = storage

        # Store document_id to response
        self.document_id = None

        # ListStore to store results
        self.result_store = Gio.ListStore()
        result_box = Gtk.ListBox()
        result_box.bind_model(self.result_store, QuickFindRow)
        result_box.connect('row-activated', self.row_activated)

        placeholder_image = Gtk.Image.new_from_icon_name("folder-saved-search-symbolic")

        placeholder_label = Gtk.Label(label=_("Quickly find documents, just start typing its name."),
                                      wrap=True,
                                      max_width_chars=32,
                                      justify=Gtk.Justification.CENTER,
                                      )
        placeholder_label.show()

        placeholder_grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                                   halign=Gtk.Align.CENTER,
                                   spacing=12,
                                   margin_top=32,
                                   )
        placeholder_grid.add_css_class("dim-label")
        placeholder_grid.append(placeholder_image)
        placeholder_grid.append(placeholder_label)

        result_box.set_placeholder(placeholder_grid)

        scrolled = Gtk.ScrolledWindow(vexpand=True,
                                      hscrollbar_policy=Gtk.PolicyType.NEVER)
        scrolled.set_child(result_box)

        self.search_entry = Gtk.SearchEntry(placeholder_text=_('Jump to...'))
        self.search_entry.connect('search-changed', self.search_changed)
        self.search_entry.connect('stop-search', self.on_stop_search)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,
                      margin_start=6, margin_end=6,
                      margin_top=6, margin_bottom=6,
                      spacing=6, )
        box.append(self.search_entry)
        box.append(scrolled)

        self.set_content(box)

        # self.connect('key_release_event', self.on_key_release_event)

    def on_stop_search(self, _sender):
        self.close()

    def search_changed(self, sender: Gtk.SearchEntry):
        self.result_store.remove_all()

        search_text = sender.get_text().strip()

        if not search_text:
            return

        documents = self.storage.find(search_text=search_text)
        for document in documents:
            self.result_store.append(document)

    def row_activated(self, sender: Gtk.ListBox, row: Gtk.ListBoxRow):
        self.emit('document-activated', row.document_id)


class QuickFindRow(Gtk.ListBoxRow):
    document_id = GObject.Property(type=int)

    def __init__(self, item: Document):
        super().__init__()

        self.document_id = item.document_id

        # Create layout box
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,
                      spacing=6,
                      margin_end=6,
                      margin_start=6,
                      margin_top=6,
                      margin_bottom=6,
                      )

        doc_label = Gtk.Label(label=item.title,
                              ellipsize=Pango.EllipsizeMode.END,
                              tooltip_text=item.title)
        archive_icon = Gtk.Image.new_from_icon_name('user-trash-symbolic')
        archive_icon.get_style_context().add_class('muted')

        box.append(doc_label)
        if item.archived:
            box.append(archive_icon)

        self.set_child(box)
