# rename_popover.py
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

from gi.repository import Gtk, Pango, GObject
from norka.define import RESOURCE_PREFIX


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/rename_popover.ui")
class RenamePopover(Gtk.Popover):
    __gtype_name__ = "RenamePopover"

    __gsignals__ = {
        "activate": (GObject.SignalFlags.ACTION, None, (str,)),
    }

    label: Gtk.Label = Gtk.Template.Child()
    entry: Gtk.Entry = Gtk.Template.Child()
    rename_btn: Gtk.Button = Gtk.Template.Child()

    def __init__(
        self,
        relative_to: Gtk.Widget,
        origin_title: str,
        label_title: str = None,
        create_mode: bool = False,
    ):
        super().__init__()
        self.set_parent(relative_to)
        self.origin_title = origin_title
        
        self.entry.set_text(origin_title)

        self.label.set_markup(
            label_title or f"<b>{_('Rename')} {self.origin_title}:</b>"
        )

        if create_mode:
            self.rename_btn.add_css_class("suggested-action")
        else:
            self.rename_btn.add_css_class("destructive-action")

    @Gtk.Template.Callback()
    def on_text_changed(self, _) -> None:
        self.rename_btn.set_sensitive(
            self.entry.get_text() and self.origin_title != self.entry.get_text()
        )

    @Gtk.Template.Callback()
    def on_apply_activated(self, widget: Gtk.Widget):
        text = self.entry.get_text().strip()
        if self.origin_title != text:
            self.emit("activate", text)
