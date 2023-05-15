# search_bar.py
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


class SearchBar(Gtk.FlowBox):
    __gsignals__ = {
        "find-changed": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "find-next": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
        "find-prev": (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__()

        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.set_column_spacing(6)
        self.set_max_children_per_line(1)
        self.add_css_class("search-bar")

        self.search_entry = Gtk.SearchEntry(hexpand=True, placeholder_text=_("Find"))
        self.search_entry.connect("changed", self.on_find_changed)
        self.search_entry.connect("activate", self.on_find_next)
        self.search_entry.connect("stop_search", self.on_stop_search)

        tool_arrow_down = Gtk.Button.new_from_icon_name("go-down-symbolic")
        tool_arrow_down.connect("clicked", self.on_find_next)

        tool_arrow_up = Gtk.Button.new_from_icon_name("go-up-symbolic")
        tool_arrow_up.connect("clicked", self.on_find_prev)

        tool_close = Gtk.Button.new_from_icon_name("window-close-symbolic")
        tool_close.connect("clicked", self.on_stop_search)

        search_grid = Gtk.Box(
            margin_bottom=3, margin_end=3, margin_start=3, margin_top=3
        )
        search_grid.add_css_class("linked")
        search_grid.append(self.search_entry)
        search_grid.append(tool_arrow_down)
        search_grid.append(tool_arrow_up)
        search_grid.append(tool_close)

        search_flow_box_child = Gtk.FlowBoxChild(can_focus=False)
        search_flow_box_child.set_child(search_grid)

        self.append(search_flow_box_child)

    def on_find_changed(self, sender, event=None):
        self.emit("find-changed", self.search_entry.get_text())

    def on_find_next(self, sender, event=None):
        self.emit("find-next", self.search_entry.get_text())

    def on_find_prev(self, sender, event=None):
        self.emit("find-prev", self.search_entry.get_text())

    def on_stop_search(self, sender: Gtk.SearchEntry) -> None:
        self.emit("stop_search")

    @GObject.Signal(flags=GObject.SignalFlags.RUN_LAST)
    def stop_search(self):
        # self.search_entry.get_style_context().remove_class(Gtk.STYLE_CLASS_ERROR)
        # self.search_entry.props.primary_icon_name = "edit-find-symbolic"
        self.search_entry.set_text("")
