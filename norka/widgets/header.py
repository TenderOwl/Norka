# header.py
#
# Copyright 2020 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written
# authorization.

from gi.repository import Gtk, Granite

from norka.define import APP_TITLE, APP_SUBTITLE


class Header(Gtk.HeaderBar):
    __gtype_name__ = 'Header'

    def __init__(self):
        super().__init__()

        self.document_mode_active = False

        self.set_title(APP_TITLE)
        self.set_subtitle(APP_SUBTITLE)
        self.set_has_subtitle(True)
        self.set_show_close_button(True)

        self.add_button = Gtk.Button.new_from_icon_name('document-new', Gtk.IconSize.LARGE_TOOLBAR)
        self.add_button.set_visible(True)
        self.add_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>n', ), 'Create new document'))
        self.add_button.set_action_name('document.create')

        self.back_button = Gtk.Button.new_with_label('Documents')
        self.back_button.get_style_context().add_class('back-button')
        self.back_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>w', ), 'Return to documents list'))
        self.back_button.set_action_name('document.close')
        self.back_button.set_visible(False)

        self.export_button = Gtk.Button.new_from_icon_name('document-export', Gtk.IconSize.LARGE_TOOLBAR)
        self.export_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>e', ), 'Export document to file'))
        self.export_button.set_visible(False)

        self.menu_button = Gtk.MenuButton()
        self.menu_button.set_tooltip_text("Menu")
        self.menu_button.set_image(Gtk.Image.new_from_icon_name('open-menu', Gtk.IconSize.LARGE_TOOLBAR))
        self.menu_button.set_visible(True)

        self.pack_start(self.back_button)
        self.pack_start(self.add_button)
        # self.pack_end(self.menu_button)
        self.pack_end(self.export_button)

    def toggle_document_mode(self) -> None:
        """Toggle document-related actions and global app actions

        :return: None
        """
        self.document_mode_active = not self.document_mode_active

        self.back_button.set_visible(self.document_mode_active)
        self.export_button.set_visible(self.document_mode_active)
        self.add_button.set_visible(not self.document_mode_active)

    def update_title(self, title: str = None) -> None:
        self.set_title(title or APP_TITLE)
