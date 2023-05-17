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

from gi.repository import Gtk, Gdk, Adw

from norka.define import RESOURCE_PREFIX
from norka.services.stats_handler import DocumentStats
from norka.widgets.menu_export import MenuExport
from norka.widgets.menu_popover import MenuPopover


class StatsMode(Enum):
    STATS = 1
    PATH = 2


@Gtk.Template(resource_path=f'{RESOURCE_PREFIX}/ui/headerbar.ui')
class NorkaHeader(Adw.Bin):
    __gtype_name__ = 'NorkaHeader'

    header_box: Gtk.Stack = Gtk.Template.Child()
    grid_header: Adw.HeaderBar = Gtk.Template.Child()
    import_button: Gtk.Button = Gtk.Template.Child()
    add_button: Gtk.Button = Gtk.Template.Child()
    add_folder_button: Gtk.Button = Gtk.Template.Child()
    back_button: Gtk.Button = Gtk.Template.Child()
    grid_menu_button: Gtk.MenuButton = Gtk.Template.Child()

    editor_header: Adw.HeaderBar = Gtk.Template.Child()
    extended_stats_button: Gtk.ToggleButton = Gtk.Template.Child()
    share_app_menu: Gtk.MenuButton = Gtk.Template.Child()
    editor_menu_button: Gtk.MenuButton = Gtk.Template.Child()

    loader_spinner: Gtk.Spinner = Gtk.Template.Child()
    editor_spinner: Gtk.Spinner = Gtk.Template.Child()
    # subtitle_path_label: Gtk.Label = Gtk.Template.Child()
    title_label: Adw.WindowTitle = Gtk.Template.Child()
    # subtitle_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        self.stats_mode = StatsMode.STATS

        self.document_mode_active = False
        self.settings = Gtk.Application.get_default().props.settings

        self.stats = None
        self.document_path = "/"

        self.header_box.set_visible_child_name("grid_header")

        # self.subtitle_eventbox.connect('button-release-event',
        #                                self.change_subtitle_mode)

        # self.search_button = Gtk.ToggleButton()
        # self.search_button.set_image(Gtk.Image.new_from_icon_name('edit-find')
        # self.search_button.set_tooltip_markup(Adw.markup_accel_tooltip(('<Control>f',), 'Find text'))
        # self.search_button.set_action_name('document.search_text')
        # self.search_button.set_visible(False)

        # self.share_app_menu: Gtk.MenuButton = self.builder.get_object(
        #     "share_app_menu")
        # self.share_app_menu.set_icon_name('document-save-as')
        # self.share_app_menu.set_popover(MenuExport(settings=self.settings))

        # self.grid_menu_button: Gtk.MenuButton = self.builder.get_object(
        #     "grid_menu_button")
        # self.grid_menu_button.set_icon_name('open-menu')
        # self.grid_menu_button.set_popover(MenuPopover(settings=self.settings))
        # self.editor_menu_button: Gtk.MenuButton = self.builder.get_object(
        #     "editor_menu_button")
        # self.editor_menu_button.set_icon_name('open-menu')
        # self.editor_menu_button.set_popover(MenuPopover(settings=self.settings))

    def toggle_document_mode(self) -> None:
        """Toggle document-related actions and global app actions

        :return: None
        """
        self.document_mode_active = not self.document_mode_active

        if self.document_mode_active:
            self.header_box.set_visible_child_name("editor_header")
        else:
            self.header_box.set_visible_child_name("grid_header")

    def update_path_label(self, path: str = "/") -> None:
        path = path.replace('/', ' > ') if path != '/' else ''
        # self.subtitle_path_label.set_label(_('root') + path)

    def update_title(self, title: str = "") -> None:
        self.title_label.set_title(title)

    def update_stats(self,
                     stats: DocumentStats = None,
                     document_path: str = None):
        self.stats = stats or self.stats
        self.document_path = document_path or self.document_path

        if self.stats_mode == StatsMode.STATS:
            label = f"{self.stats.characters} chars | {self.stats.words} words"
        elif self.stats_mode == StatsMode.PATH:

            path = self.document_path.replace('/', ' > ') if self.document_path != '/' else ''
            label = _('root') + path
        else:
            label = ""

        # tooltip_text = _('Click to switch between <b>stats</b> and <b>path</b>')
        # tooltip = f'\n<span weight="600" size="smaller" alpha="75%">{tooltip_text}</span>'

        # self.subtitle_label.set_label(label)
        # self.subtitle_label.set_tooltip_markup(label + tooltip)

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

    def change_subtitle_mode(self, sender: Gtk.Label,
                             button) -> bool:
        if button.button == Gdk.BUTTON_PRIMARY:
            self.stats_mode = StatsMode.PATH if self.stats_mode == StatsMode.STATS else StatsMode.STATS
            self.update_stats()
        return True
