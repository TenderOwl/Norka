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

from gi.repository import Gtk, Granite


class MenuPopover(Gtk.Popover):
    def __init__(self, settings):
        super().__init__()
        self.set_constrain_to(Gtk.PopoverConstraint.NONE)

        self.settings = settings

        zoom_out_button = Gtk.Button.new_from_icon_name("zoom-out-symbolic", Gtk.IconSize.MENU)
        zoom_out_button.set_action_name('document.zoom_out')
        zoom_out_button.set_tooltip_markup(
            Granite.markup_accel_tooltip(('<Control>minus',), _('Zoom Out')))

        self.zoom_default_button = Gtk.Button("100%", action_name='document.zoom_default')
        self.zoom_default_button.set_tooltip_markup(
            Granite.markup_accel_tooltip(('<Control>0',), _('Zoom 1:1')))

        zoom_in_button = Gtk.Button.new_from_icon_name("zoom-in-symbolic", Gtk.IconSize.MENU)
        zoom_in_button.set_action_name('document.zoom_in')
        zoom_in_button.set_tooltip_markup(
            Granite.markup_accel_tooltip(('<Control>equal', '<Control>plus'), _('Zoom In')))

        font_size_grid = Gtk.Grid(column_homogeneous=True, hexpand=True, margin=12)
        font_size_grid.get_style_context().add_class(Gtk.STYLE_CLASS_LINKED)
        font_size_grid.add(zoom_out_button)
        font_size_grid.add(self.zoom_default_button)
        font_size_grid.add(zoom_in_button)

        preferences_menuitem = Gtk.ModelButton(
            text=_("Preferences"),
            action_name='app.preferences')
        preferences_menuitem.get_child().destroy()
        preferences_menuitem.add(Granite.AccelLabel.from_action_name("Preferences", "app.preferences"))

        about_menuitem = Gtk.ModelButton(
            text=_("About"),
            action_name='app.about')

        preview_menuitem = Gtk.ModelButton(
            text=_("Preview"),
            action_name='document.preview')
        preview_menuitem.get_child().destroy()
        preview_menuitem.add(Granite.AccelLabel.from_action_name("Preview", "document.preview"))

        shortcuts_menuitem = Gtk.ModelButton(
            text=_("Shortcuts"),
            action_name='app.shortcuts')
        format_shortcuts_menuitem = Gtk.ModelButton(
            text=_("Markup Shortcuts"),
            action_name='app.format_shortcuts')
        quit_menuitem = Gtk.ModelButton(
            text=_("Quit"),
            action_name='app.quit')
        quit_menuitem.get_child().destroy()
        quit_menuitem.add(Granite.AccelLabel.from_action_name("Quit", "app.quit"))

        menu_grid = Gtk.Grid(margin_bottom=3, orientation=Gtk.Orientation.VERTICAL, width_request=200)
        menu_grid.attach(font_size_grid, 0, 0, 3, 1)
        menu_grid.attach(self.make_sep(), 0, 1, 3, 1)
        menu_grid.attach(preferences_menuitem, 0, 2, 3, 1)
        menu_grid.attach(preview_menuitem, 0, 3, 3, 1)
        menu_grid.attach(self.make_sep(), 0, 4, 3, 1)
        menu_grid.attach(format_shortcuts_menuitem, 0, 5, 3, 1)
        menu_grid.attach(shortcuts_menuitem, 0, 6, 3, 1)
        menu_grid.attach(about_menuitem, 0, 7, 3, 1)
        menu_grid.attach(self.make_sep(), 0, 8, 3, 1)
        menu_grid.attach(quit_menuitem, 0, 9, 3, 1)

        self.add(menu_grid)

        menu_grid.show_all()

        self.zoom_default_button.set_label(f"{settings.get_int('zoom')}%")
        self.settings.connect('changed', self.on_settings_changed)

    def on_settings_changed(self, settings, key):
        if key == 'zoom':
            self.zoom_default_button.set_label(f"{settings.get_int('zoom')}%")

    @staticmethod
    def make_sep():
        return Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL,
                             margin_top=6,
                             margin_bottom=6)
