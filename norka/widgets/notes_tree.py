# MIT License
#
# Copyright (c) 2025 Andrey Maksimov
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
from typing import Optional

from gi.repository import Gio, Pango, Gtk, GObject, Gdk, GLib
from loguru import logger

from norka.define import RESOURCE_PREFIX
from norka.models import AppState, Folder, Document
from norka.services import Storage


class TreeNode(GObject.Object):
    def __init__(self, item: Folder|Document, depth=0):
        super().__init__()
        self.item = item
        self.depth = depth
        self.is_folder = isinstance(item, Folder)


class TreeWidget(Gtk.TreeExpander):
    def __init__(self):
        super().__init__()
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.icon = Gtk.Image()
        self.label: Gtk.Label = Gtk.Label(
            ellipsize=Pango.EllipsizeMode.END, halign=Gtk.Align.START
        )

        self.box.append(self.icon)
        self.box.append(self.label)
        self.set_child(self.box)


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/notes_tree.ui")
class NotesTree(Gtk.Box):
    __gtype_name__ = "NotesTree"

    # Signals
    __gsignals__ = {
        "item-activate": (GObject.SIGNAL_ACTION, None, (TreeNode,)),
    }

    # Properties
    _storage: Optional[Storage]
    _appstate: Optional[AppState]
    _current_path = '/'
    _selected_node: Optional[TreeNode]

    # Child Widgets
    list_view: Gtk.ListView = Gtk.Template.Child()
    tree_model: Gtk.TreeListModel
    root_store: Gio.ListStore
    selection: Gtk.SingleSelection = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self._appstate = Gtk.Application.get_default().props.appstate
        self._appstate.connect('document-changed', self._select_node)

        self._storage = Gtk.Application.get_default().props.storage
        self._storage.connect('items-changed', lambda _x: self.load_tree())

        self.root_store = Gio.ListStore(item_type=TreeNode)
        self.tree_model = Gtk.TreeListModel.new(
            self.root_store,
            passthrough=False,
            autoexpand=False,
            create_func=self._create_child_model,
        )
        self.selection.set_model(self.tree_model)

    def _create_child_model(self, node: TreeNode):
        if not node.is_folder:
            return None

        folder: Folder = node.item
        children = Gio.ListStore(item_type=TreeNode)

        # Load child folders
        for child_folder in self._storage.get_child_folders(folder):
            logger.debug('Loading child folder {}', child_folder)
            children.append(TreeNode(child_folder, node.depth + 1))

        # Load child documents
        for doc in self._storage.get_child_docs(folder):
            logger.debug('Loading child document {}', doc)
            children.append(TreeNode(doc, node.depth + 1))

        if children.get_n_items() > 0:
            return children

        return None

    def _select_node(self, appstate: AppState, doc_id: str):
        # self.load_tree()
        for i in range(self.root_store.get_n_items()):
            row = self.root_store.get_item(i)
            if not row.is_folder and str(row.item.document_id) == doc_id:
                self.selection.select_item(i, unselect_rest=True)
                break

    @Gtk.Template.Callback()
    def _on_selection_changed(self, select: Gtk.SelectionModel, position: int, _n_times: int):
        if row := select.get_selected_item():
            self._selected_node = row.get_item()
            if not self._selected_node.is_folder:
                self.activate_action(
                    "document.open",
                    GLib.Variant.new_string(str(self._selected_node.item.document_id)),
                )
            else:
                self.emit("item-activate", self._selected_node)
                # self.load_tree(path=self._selected_node.item.absolute_path)
                self._appstate.current_path = str(self._selected_node.item.path)
        else:
            self._selected_node = None

        self._appstate.current_document_id = None

    def load_tree(self, path:str = None):
        if path:
            self._current_path = path
        root_folders = self._storage.get_folders(path=self._current_path)
        root_docs = self._storage.all(path=self._current_path)

        # Remove old items only if new items available
        if root_folders or root_docs:
            self.root_store.remove_all()

        for folder in root_folders:
            self.root_store.append(TreeNode(folder))

        for doc in root_docs:
            self.root_store.append(TreeNode(doc))

    @Gtk.Template.Callback()
    def _on_item_setup(self, _, list_item: Gtk.ListItem):
        # expander = Gtk.TreeExpander()
        # box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        # icon = Gtk.Image()
        # label = Gtk.Label(ellipsize=Pango.EllipsizeMode.END, halign=Gtk.Align.START)
        # box.append(expander)
        # box.append(icon)
        # box.append(label)
        # expander.set_child(box)
        # controller = Gtk.GestureClick()
        # controller.connect_data('released', self._activate, list_item)
        # expander.add_controller(controller)
        widget: TreeWidget = TreeWidget()
        list_item.set_child(widget)

    @Gtk.Template.Callback()
    def _on_item_bind(self, _: Gtk.ListView, list_item: Gtk.ListItem):
        node = list_item.get_item().get_item()
        widget: TreeWidget = list_item.get_child()
        # expander = box.expander
        # icon, label = box.get_first_child(), box.get_last_child()

        # Настройка отступа
        widget.set_margin_start(node.depth * 24)

        if node.is_folder:
            widget.set_list_row(list_item.get_item())
            widget.icon.set_from_icon_name("folder-symbolic")
            widget.label.set_label(node.item.title)
        else:
            widget.icon.set_from_icon_name("x-office-document-symbolic")
            widget.label.set_label(node.item.title)

    def _activate(self, click: Gtk.GestureClick, _n_press: int, _x: float, _y: float, list_item) -> None:
        button = click.get_current_button()
        if button == Gdk.BUTTON_PRIMARY and (node := list_item.get_item().get_item()):
            if not node.is_folder:
                self.activate_action('document.open', GLib.Variant.new_string(str(node.item.document_id)),)

