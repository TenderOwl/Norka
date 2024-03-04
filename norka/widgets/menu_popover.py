# menu_popover.py
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

from gi.repository import Gtk

from norka.define import RESOURCE_PREFIX
from norka.utils import markup_accel_tooltip


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/menu_popover.ui")
class MenuPopover(Gtk.Popover):
    __gtype_name__ = 'EditorMenuPopover'

    zoom_out_button: Gtk.Button = Gtk.Template.Child()
    zoom_default_button: Gtk.Button = Gtk.Template.Child()
    zoom_in_button: Gtk.Button = Gtk.Template.Child()

    preferences_menuitem: Gtk.Button = Gtk.Template.Child()
    preview_menuitem: Gtk.Button = Gtk.Template.Child()
    shortcuts_menuitem: Gtk.Button = Gtk.Template.Child()
    format_shortcuts_menuitem: Gtk.Button = Gtk.Template.Child()
    about_menuitem: Gtk.Button = Gtk.Template.Child()
    backup_menuitem: Gtk.Button = Gtk.Template.Child()
    quit_menuitem: Gtk.Button = Gtk.Template.Child()

    def __init__(self, settings):
        super().__init__()
        # self.set_constrain_to(Gtk.PopoverConstraint.NONE)

        self.settings = settings

        # zoom_out_button = Gtk.Button.new_from_icon_name("zoom-out-symbolic")
        # zoom_out_button.set_action_name('document.zoom_out')
        self.zoom_out_button.set_tooltip_markup(
            markup_accel_tooltip(('<Control>minus',), _('Zoom Out')))
        #
        # self.zoom_default_button = Gtk.Button(label="100%", action_name='document.zoom_default')
        self.zoom_default_button.set_tooltip_markup(
            markup_accel_tooltip(('<Control>0',), _('Zoom 1:1')))
        #
        # zoom_in_button = Gtk.Button.new_from_icon_name("zoom-in-symbolic")
        # zoom_in_button.set_action_name('document.zoom_in')
        self.zoom_in_button.set_tooltip_markup(
            markup_accel_tooltip(('<Control>equal', '<Control>plus'), _('Zoom In')))
        #
        # font_size_grid = Gtk.Grid(column_homogeneous=True, hexpand=True, margin_top=6)
        # font_size_grid.add_css_class('linked')
        # font_size_grid.attach(zoom_out_button, 0, 0, 1, 1)
        # font_size_grid.attach(self.zoom_default_button, 1, 0, 1, 1)
        # font_size_grid.attach(zoom_in_button, 2, 0, 1, 1)
        #
        # preferences_menuitem = Gtk.Button(label=_('Preferences'), action_name='app.preferences')
        #
        # about_menuitem = Gtk.Button(label=_("About"), action_name='app.about')
        #
        # preview_menuitem = Gtk.Button(label=_("Preview"), action_name='document.preview')
        #
        # shortcuts_menuitem = Gtk.Button(label=_("Shortcuts"), action_name='app.shortcuts')
        # format_shortcuts_menuitem = Gtk.Button(label=_("Markup Shortcuts"), action_name='app.format_shortcuts')
        #
        # backup_menuitem = Gtk.Button(label=_("Make backup"), action_name='document.backup')
        #
        # quit_menuitem = Gtk.Button(label=_("Quit"), action_name='app.quit')
        #
        # menu_grid = Gtk.Grid(orientation=Gtk.Orientation.VERTICAL, width_request=200,
        #                      margin_bottom=6, margin_start=6, margin_end=6)
        # menu_grid.attach(font_size_grid, 0, 0, 3, 1)
        # menu_grid.attach(self.make_sep(), 0, 1, 3, 1)
        # menu_grid.attach(preferences_menuitem, 0, 2, 3, 1)
        # menu_grid.attach(preview_menuitem, 0, 3, 3, 1)
        # menu_grid.attach(self.make_sep(), 0, 4, 3, 1)
        # menu_grid.attach(format_shortcuts_menuitem, 0, 5, 3, 1)
        # menu_grid.attach(shortcuts_menuitem, 0, 6, 3, 1)
        # menu_grid.attach(about_menuitem, 0, 7, 3, 1)
        # menu_grid.attach(self.make_sep(), 0, 8, 3, 1)
        # menu_grid.attach(backup_menuitem, 0, 9, 3, 1)
        # menu_grid.attach(self.make_sep(), 0, 10, 3, 1)
        # menu_grid.attach(quit_menuitem, 0, 11, 3, 1)
        #
        # self.set_child(menu_grid)

        # self.zoom_default_button.set_label(f"{settings.get_int('zoom')}%")
        self.settings.connect('changed', self.on_settings_changed)

    def on_settings_changed(self, settings, key):
        if key == 'zoom':
            self.zoom_default_button.set_label(f"{settings.get_int('zoom')}%")

    @staticmethod
    def make_sep():
        return Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL,
                             margin_top=6,
                             margin_bottom=6)
