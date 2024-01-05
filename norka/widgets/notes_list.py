# MIT License
#
# Copyright (c) 2023 Andrey Maksimov
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
#
# SPDX-License-Identifier: MIT

from gi.repository import Gtk, Gio, Pango
from loguru import logger

from norka.define import RESOURCE_PREFIX
from norka.document_manager import document_manager
from norka.models.document import Document
from norka.services.settings import Settings
from norka.services.storage import Storage


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/notes_list.ui')
class NotesList(Gtk.Box):
    __gtype_name__ = 'NotesList'

    list_view: Gtk.ListView = Gtk.Template.Child()
    selection: Gtk.SingleSelection = Gtk.Template.Child()
    filter_model: Gtk.FilterListModel = Gtk.Template.Child()
    store: Gio.ListStore = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.settings: Settings = Gtk.Application.get_default().props.settings
        self.storage: Storage = Gtk.Application.get_default().props.storage

    def reload_notes(self, path: str = "/", include_archived: bool = False):
        documents = self.storage.all(path=path, with_archived=include_archived)

        if documents:
            self.store.remove_all()
            for doc in documents:
                self.store.append(doc)

    @Gtk.Template.Callback()
    def _on_item_setup(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem):
        label = Gtk.Label(ellipsize=Pango.EllipsizeMode.END, xalign=0, hexpand=True)
        list_item.set_child(label)

    @Gtk.Template.Callback()
    def _on_item_bind(self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem):
        label: Gtk.Label = list_item.get_child()
        document: Document = list_item.get_item()
        label.set_label(document.title)
        label.set_tooltip_markup(f'<b>{document.title}</b>\n<small>{document.absolute_path}</small>')

    @Gtk.Template.Callback()
    def _on_list_view_activate(self, list_view: Gtk.ListView, position: int):
        selected_item = self.store.get_item(position)
        logger.debug(f"_on_list_view_activate: {selected_item}")
        document_manager.current_document = selected_item
