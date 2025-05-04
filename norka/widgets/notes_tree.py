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

from gi.repository import Gio, Pango, Gtk, GObject, Gdk, GLib

from norka.define import RESOURCE_PREFIX
from norka.models import Folder, Document


class TreeNode(GObject.Object):
    def __init__(self, item: Folder|Document, depth=0):
        super().__init__()
        self.item = item
        self.depth = depth
        self.is_folder = isinstance(item, Folder)


class TreeWidget(Gtk.Box):
    def __init__(self):
        super().__init__(
            spacing=6, margin_start=6, margin_end=12, margin_top=6, margin_bottom=6
        )

        self.expander = Gtk.TreeExpander()

        self.icon = Gtk.Image()
        self.label: Gtk.Label = Gtk.Label(
            ellipsize=Pango.EllipsizeMode.END, halign=Gtk.Align.START
        )

        self.append(self.expander)
        self.append(self.label)


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/notes_tree.ui")
class NotesTree(Gtk.Box):
    __gtype_name__ = "NotesTree"

    # Signals
    __gsignals__ = {
        "item-activate": (GObject.SIGNAL_ACTION, None, (TreeNode,)),
    }

    # Properties
    _current_path = '/'

    # Child Widgets
    list_view: Gtk.ListView = Gtk.Template.Child()
    tree_model: Gtk.TreeListModel
    root_store: Gio.ListStore
    selection: Gtk.SingleSelection = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.storage = Gtk.Application.get_default().props.storage

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

        # Загрузка подпапок
        for child_folder in self.storage.get_folders(folder.path):
            children.append(TreeNode(child_folder, node.depth + 1))

        return None

    def load_tree(self, path:str = None):
        if path:
            self._current_path = path
        root_folders = self.storage.get_folders(path=self._current_path)
        for folder in root_folders:
            self.root_store.append(TreeNode(folder))

        root_docs = self.storage.all(path=self._current_path)
        for doc in root_docs:
            self.root_store.append(TreeNode(doc))

    # @Gtk.Template.Callback()
    def _on_list_view_activate(self, sender, _):
        position = self.selection.get_selected()
        row: Gtk.TreeListRow = self.tree_model.get_item(position)
        if row:
            item: TreeNode = row.get_item()
            print(item.item)
            self.emit("item-activate", item)

    @Gtk.Template.Callback()
    def _on_item_setup(self, _, list_item: Gtk.ListItem):
        expander = Gtk.TreeExpander()
        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        icon = Gtk.Image()
        label = Gtk.Label(ellipsize=Pango.EllipsizeMode.END, halign=Gtk.Align.START)
        box.append(icon)
        box.append(label)
        expander.set_child(box)
        controller = Gtk.GestureClick()
        controller.connect_data('released', self._activate, list_item)
        expander.add_controller(controller)
        list_item.set_child(expander)

    @Gtk.Template.Callback()
    def _on_item_bind(self, _: Gtk.ListView, list_item: Gtk.ListItem):
        node = list_item.get_item().get_item()
        expander = list_item.get_child()
        box = expander.get_child()
        icon, label = box.get_first_child(), box.get_last_child()

        # Настройка отступа
        # expander.set_margin_start(node.depth * 24)

        if node.is_folder:
            expander.set_list_row(list_item.get_item())
            icon.set_from_icon_name("folder-symbolic")
            label.set_label(node.item.title)
        else:
            icon.set_from_icon_name("x-office-document-symbolic")
            label.set_label(node.item.title)

    def _activate(self, click: Gtk.GestureClick, _n_press: int, _x: float, _y: float, list_item) -> None:
        button = click.get_current_button()
        if button == Gdk.BUTTON_PRIMARY and (node := list_item.get_item().get_item()):
            if not node.is_folder:
                self.activate_action('document.open', GLib.Variant.new_string(str(node.item.document_id)),)

