# header.py
#
# MIT License
#
# Copyright (c) 2020-2021 Andrey Maksimov <meamka@ya.ru>
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

from enum import Enum
from gettext import gettext as _

from gi.repository import Gtk, Gdk, Granite, Handy

from norka.define import RESOURCE_PREFIX
from norka.services.stats_handler import DocumentStats
from norka.widgets.menu_export import MenuExport
from norka.widgets.menu_popover import MenuPopover


class StatsMode(Enum):
    STATS = 1
    PATH = 2


class Header(Gtk.Box):
    __gtype_name__ = 'Header'

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)

        self.builder = Gtk.Builder.new_from_resource(
            f'{RESOURCE_PREFIX}/ui/headerbar.ui'
        )
        self.header_box: Gtk.Stack = self.builder.get_object('header_box')
        self.grid_header: Handy.HeaderBar = self.builder.get_object('grid_header')
        self.editor_header: Handy.HeaderBar = self.builder.get_object('editor_header')
        self.loader_spinner: Gtk.Spinner = self.builder.get_object('loader_spinner')
        self.editor_spinner: Gtk.Spinner = self.builder.get_object('editor_spinner')
        self.title_label: Gtk.Label = self.builder.get_object('title_label')
        self.subtitle_label: Gtk.Label = self.builder.get_object('subtitle_label')
        self.subtitle_eventbox: Gtk.EventBox = self.builder.get_object('subtitle_eventbox')

        self.stats_mode = StatsMode.STATS

        self.document_mode_active = False
        self.settings = settings

        self.stats = None
        self.document_path = "/"

        self.header_box.set_visible_child_name("grid_header")
        self.add(self.header_box)

        self.subtitle_eventbox.connect('button-release-event', self.change_subtitle_mode)

        self.import_button: Gtk.Button = self.builder.get_object("import_button")
        self.import_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>o',), _('Import file to Norka')))
        #
        self.add_button: Gtk.Button = self.builder.get_object("add_button")
        self.add_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>n',), _('Create new document')))

        self.add_folder_button: Gtk.Button = self.builder.get_object("add_folder_button")
        self.add_folder_button.set_tooltip_markup(
            Granite.markup_accel_tooltip(('<Control><Shift>n',), _('Create new folder')))

        self.back_button: Gtk.Button = self.builder.get_object("back_button")
        self.back_button.set_tooltip_markup(Granite.markup_accel_tooltip(
            ('<Control>w',),
            _('Save document and return to documents list')))

        # # self.search_button = Gtk.ToggleButton()
        # # self.search_button.set_image(Gtk.Image.new_from_icon_name('edit-find', Gtk.IconSize.LARGE_TOOLBAR))
        # # self.search_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>f',), 'Find text'))
        # # self.search_button.set_action_name('document.search_text')
        # # self.search_button.set_visible(False)

        self.print_button: Gtk.ToggleButton() = self.builder.get_object("print_button")
        self.print_button.set_tooltip_markup(Granite.markup_accel_tooltip(('<Control>p',), _('Print the document')))

        self.extended_stats_button: Gtk.ToggleButton() = self.builder.get_object("extended_stats_button")
        self.extended_stats_button.set_tooltip_markup(Granite.markup_accel_tooltip(None, _('Show document info')))

        self.share_app_menu: Gtk.MenuButton = self.builder.get_object("share_app_menu")
        self.share_app_menu.set_image(Gtk.Image.new_from_icon_name('document-save-as', Gtk.IconSize.LARGE_TOOLBAR))
        self.share_app_menu.set_popover(MenuExport(settings=self.settings))

        self.archived_button: Gtk.ToggleButton() = self.builder.get_object("archived_button")
        self.archived_button.set_tooltip_markup(Granite.markup_accel_tooltip(None, _('Show Archived files')))

        self.grid_menu_button: Gtk.MenuButton = self.builder.get_object("grid_menu_button")
        self.grid_menu_button.set_image(Gtk.Image.new_from_icon_name('open-menu', Gtk.IconSize.LARGE_TOOLBAR))
        self.grid_menu_button.set_popover(MenuPopover(settings=self.settings))
        self.editor_menu_button: Gtk.MenuButton = self.builder.get_object("editor_menu_button")
        self.editor_menu_button.set_image(Gtk.Image.new_from_icon_name('open-menu', Gtk.IconSize.LARGE_TOOLBAR))
        self.editor_menu_button.set_popover(MenuPopover(settings=self.settings))

    def toggle_document_mode(self) -> None:
        """Toggle document-related actions and global app actions

        :return: None
        """
        self.document_mode_active = not self.document_mode_active

        if self.document_mode_active:
            self.header_box.set_visible_child_name("editor_header")
        else:
            self.header_box.set_visible_child_name("grid_header")

    def update_title(self, title: str = "") -> None:
        self.title_label.set_label(title)

    def update_stats(self, stats: DocumentStats = None, document_path: str = None):
        self.stats = stats or self.stats
        self.document_path = document_path or self.document_path

        if self.stats_mode == StatsMode.STATS:
            label = f"{self.stats.characters} chars | {self.stats.words} words"
        elif self.stats_mode == StatsMode.PATH:
            label = self.document_path
        else:
            label = ""

        self.subtitle_label.set_label(label)

    def show_spinner(self, state: bool = False) -> None:
        # Gonna fix this double spinners
        if state:
            self.loader_spinner.start()
            self.editor_spinner.start()
        else:
            self.editor_spinner.stop()
            self.loader_spinner.stop()
        self.loader_spinner.set_visible(state)
        self.editor_spinner.set_visible(state)

    def change_subtitle_mode(self, sender: Gtk.Label, button: Gdk.EventButton) -> bool:
        if button.button == Gdk.BUTTON_PRIMARY:
            self.stats_mode = StatsMode.PATH if self.stats_mode == StatsMode.STATS else StatsMode.STATS
            self.update_stats()
        return True
