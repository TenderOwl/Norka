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

from gi.repository import Gtk, Adw


class MenuPopover(Gtk.Popover):
    __gtype_name__ = 'EditorMenuPopover'

    def __init__(self, settings):
        super().__init__()

        self.settings = settings

        zoom_out_button = Gtk.Button.new_from_icon_name("zoom-out-symbolic")
        zoom_out_button.set_action_name('document.zoom_out')
        # zoom_out_button.set_tooltip_markup(
        #     Granite.markup_accel_tooltip(('<Control>minus',), _('Zoom Out')))

        self.zoom_default_button = Gtk.Button(label="100%", action_name='document.zoom_default')
        # self.zoom_default_button.set_tooltip_markup(
        #     Granite.markup_accel_tooltip(('<Control>0',), _('Zoom 1:1')))

        zoom_in_button = Gtk.Button.new_from_icon_name("zoom-in-symbolic")
        zoom_in_button.set_action_name('document.zoom_in')
        # zoom_in_button.set_tooltip_markup(
        #     Granite.markup_accel_tooltip(('<Control>equal', '<Control>plus'), _('Zoom In')))

        font_size_grid = Gtk.Box(homogeneous=True, hexpand=True, margin_top=6)
        font_size_grid.add_css_class('linked')
        font_size_grid.append(zoom_out_button)
        font_size_grid.append(self.zoom_default_button)
        font_size_grid.append(zoom_in_button)

        preferences_menuitem = Gtk.Button(label=_('Preferences'), action_name='app.preferences')
        about_menuitem = Gtk.Button(label=_("About"), action_name='app.about')
        preview_menuitem = Gtk.Button(label=_("Preview"),action_name='document.preview')

        shortcuts_menuitem = Gtk.Button(label=_("Shortcuts"), action_name='app.shortcuts')
        format_shortcuts_menuitem = Gtk.Button(label=_("Markup Shortcuts"), action_name='app.format_shortcuts')
        backup_menuitem = Gtk.Button(label=_("Make backup"), action_name='document.backup')

        quit_menuitem = Gtk.Button(label=_("Quit"), action_name='app.quit')

        menu_grid = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, width_request=200,
                             margin_bottom=6, margin_start=6, margin_end=6)
        menu_grid.append(font_size_grid)
        menu_grid.append(self.make_sep())
        menu_grid.append(preferences_menuitem)
        menu_grid.append(preview_menuitem)
        menu_grid.append(self.make_sep())
        menu_grid.append(format_shortcuts_menuitem)
        menu_grid.append(shortcuts_menuitem)
        menu_grid.append(about_menuitem)
        menu_grid.append(self.make_sep())
        menu_grid.append(backup_menuitem)
        menu_grid.append(self.make_sep())
        menu_grid.append(quit_menuitem)

        self.set_child(menu_grid)

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
