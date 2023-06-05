# message_dialog.py
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

from gi.repository import Gtk, Gio

from norka.define import APP_TITLE


class MessageDialog(Gtk.MessageDialog):
    __gtype_name__ = 'DeleteDialog'

    def __init__(self, primary_text: str, secondary_text: str, image_icon_name: str,
                 buttons: Gtk.ButtonsType = Gtk.ButtonsType.NONE):
        super().__init__(
            text=primary_text,
            secondary_text=secondary_text,
            buttons=buttons,
            message_type=Gtk.MessageType.WARNING
        )
        # self.set_image_icon(Gio.ThemedIcon.new(image_icon_name))
        self.set_title(APP_TITLE)
        self.set_transient_for(Gtk.Application.get_default().props.active_window)

        self.add_button(_('Cancel'), Gtk.ResponseType.CANCEL)
        self.add_button(_('Delete'), Gtk.ResponseType.APPLY)

        self.set_default_response(Gtk.ResponseType.CANCEL)
        self.get_widget_for_response(Gtk.ResponseType.APPLY).get_style_context().add_class("destructive-action")
