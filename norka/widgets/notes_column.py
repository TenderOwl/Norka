# notes_column.py
#
# MIT License
#
# Copyright (c) 2025 Andrey Maksimov <meamka@ya.ru>
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
from gi.repository import Gtk, Adw
from loguru import logger

from norka.define import RESOURCE_PREFIX
from norka.widgets.notes_tree import  NotesTree


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/notes_column.ui")
class NotesColumn(Gtk.Box):
    __gtype_name__ = 'NotesColumn'

    notes_tree: NotesTree = Gtk.Template.Child()
    view_switcher: Adw.InlineViewSwitcher = Gtk.Template.Child()
    columns_stack: Adw.ViewStack = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Reload child widget content when widget is shown
        self.columns_stack.connect('notify::visible-child-name', self._on_visible_view_changed)

        self.notes_tree.load_tree()

    def _on_visible_view_changed(self, sender, data):
        visible_page = self.columns_stack.get_visible_child_name()
        match visible_page:
            case 'tree_view':
                child: NotesTree = self.columns_stack.get_visible_child()
                child.load_tree()
            case 'structure_view':
                # child: NotesTree = self.columns_stack.get_visible_child()
                # child.load_tree()
                logger.debug('structure_view')