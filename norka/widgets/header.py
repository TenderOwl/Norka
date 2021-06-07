# header.py
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

from gi.repository import Gtk, Granite, Handy

from norka.define import APP_TITLE, APP_SUBTITLE
from norka.widgets.menu_export import MenuExport
from norka.widgets.menu_popover import MenuPopover


class Header(Handy.HeaderBar):
    __gtype_name__ = 'Header'

    def __init__(self, settings):
        super().__init__()

        self.document_mode_active = False
        self.settings = settings

        self.set_title(_("Norka"))
        self.set_subtitle(APP_SUBTITLE)
        self.set_has_subtitle(True)
        self.set_show_close_button(True)
        self.get_style_context().add_class('norka-header')

        self.spinner = Gtk.Spinner(visible=False)

        self.import_button = Gtk.Button.new_from_icon_name('document-open', Gtk.IconSize.LARGE_TOOLBAR)
        self.import_button.set_visible(True)
        self.import_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>o',), _('Import file to Norka')))
        self.import_button.set_action_name('document.import')

        self.add_button = Gtk.Button.new_from_icon_name('document-new', Gtk.IconSize.LARGE_TOOLBAR)
        self.add_button.set_visible(True)
        self.add_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>n',), _('Create new document')))
        self.add_button.set_action_name('document.create')

        self.back_button = Gtk.Button.new_with_label(_('Documents'))
        self.back_button.set_valign(Gtk.Align.CENTER)
        self.back_button.get_style_context().add_class('back-button')
        self.back_button.set_tooltip_markup(Granite.markup_accel_tooltip(
            ('<Control>w',),
            _('Save document and return to documents list')))
        self.back_button.set_visible(False)
        self.back_button.set_action_name('document.close')

        # self.search_button = Gtk.ToggleButton()
        # self.search_button.set_image(Gtk.Image.new_from_icon_name('edit-find', Gtk.IconSize.LARGE_TOOLBAR))
        # self.search_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>f',), 'Find text'))
        # self.search_button.set_action_name('document.search_text')
        # self.search_button.set_visible(False)

        self.share_app_menu = Gtk.MenuButton(tooltip_text=_("Share"))
        self.share_app_menu.set_image(Gtk.Image.new_from_icon_name('document-save-as', Gtk.IconSize.LARGE_TOOLBAR))
        self.share_app_menu.set_popover(MenuExport(settings=self.settings))

        self.archived_button = Gtk.ToggleButton()
        self.archived_button.set_image(Gtk.Image.new_from_icon_name('user-trash', Gtk.IconSize.LARGE_TOOLBAR))
        self.archived_button.set_tooltip_markup(Granite.markup_accel_tooltip(None, _('Show Archived files')))
        self.archived_button.set_action_name('document.toggle_archived')
        self.archived_button.set_visible(True)

        self.menu_button = Gtk.MenuButton(tooltip_text=_("Menu"))
        self.menu_button.set_image(Gtk.Image.new_from_icon_name('open-menu', Gtk.IconSize.LARGE_TOOLBAR))
        self.menu_button.set_popover(MenuPopover(settings=self.settings))
        self.menu_button.set_visible(True)

        self.pack_start(self.back_button)
        self.pack_start(self.add_button)
        self.pack_start(self.import_button)
        self.pack_start(self.spinner)
        self.pack_end(self.menu_button)
        self.pack_end(self.share_app_menu)
        self.pack_end(self.archived_button)
        # self.pack_end(self.search_button)

    def toggle_document_mode(self) -> None:
        """Toggle document-related actions and global app actions

        :return: None
        """
        self.document_mode_active = not self.document_mode_active

        self.back_button.set_visible(self.document_mode_active)
        # self.search_button.set_visible(self.document_mode_active)
        self.share_app_menu.set_visible(self.document_mode_active)
        self.add_button.set_visible(not self.document_mode_active)
        self.import_button.set_visible(not self.document_mode_active)
        self.archived_button.set_visible(not self.document_mode_active)

    def update_title(self, title: str = None) -> None:
        self.set_title(title or APP_TITLE)

    def show_spinner(self, state: bool = False) -> None:
        if state:
            self.spinner.start()
        else:
            self.spinner.stop()
        self.spinner.set_visible(state)
