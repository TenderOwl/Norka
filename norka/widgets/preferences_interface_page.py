# preferences_interface_page.py
#
# MIT License
#
# Copyright (c) 2025 Andrey Maksimov <meamka@ya.ru>
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
from typing import Optional

from gi.repository import Adw, Gtk, GtkSource
from loguru import logger

from norka.define import RESOURCE_PREFIX
from norka.services import Settings


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/preferences_interface_page.ui")
class PreferencesInterfacePage(Adw.PreferencesPage):
    __gtype_name__ = 'PreferencesInterfacePage'

    theme_toggle: Adw.ToggleGroup = Gtk.Template.Child()
    styles_group: Adw.PreferencesGroup = Gtk.Template.Child()
    style_chooser: GtkSource.StyleSchemeChooserWidget

    _settings: Settings
    _style_manager: Optional[Adw.StyleManager]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._settings = Gtk.Application.get_default().props.settings
        self._style_manager = Adw.StyleManager.get_default()

        self.theme_toggle.set_active_name(self._settings.get_string("theme-mode") or "system")
        self.theme_toggle.connect("notify::active-name", self._on_theme_toggled)

        self.style_chooser = GtkSource.StyleSchemeChooserWidget()
        self.style_chooser.connect("notify::style-scheme", self._on_scheme_changed)
        self.styles_group.add(self.style_chooser)

    def _on_theme_toggled(self, _sender, _data):
        theme_mode = self.theme_toggle.get_active_name()
        logger.debug(f'Apply theme: {theme_mode}')
        match theme_mode:
            case "light":
                self._style_manager.set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
            case "dark":
                self._style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)
            case _:
                self._style_manager.set_color_scheme(Adw.ColorScheme.DEFAULT)

        self._settings.set_string("theme-mode", theme_mode)

    def _on_scheme_changed(self, _sender, _data):
        self._settings.set_string('stylescheme', self.style_chooser.get_style_scheme().get_id())