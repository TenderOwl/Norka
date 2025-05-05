# preferences_general_page.py
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
from gi.repository import Adw, Gtk, Gio

from norka.define import RESOURCE_PREFIX
from norka.services import Settings


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/preferences_general_page.ui")
class PreferencesGeneralPage(Adw.PreferencesPage):
    __gtype_name__ = 'PreferencesGeneralPage'

    autosave_switch: Adw.SwitchRow = Gtk.Template.Child()
    sort_switch: Adw.SwitchRow = Gtk.Template.Child()
    spellcheck_switch: Adw.SwitchRow = Gtk.Template.Child()
    spellcheck_language_chooser: Adw.ComboRow = Gtk.Template.Child()
    autoindent_switch: Adw.SwitchRow = Gtk.Template.Child()
    spaces_tabs_switch: Adw.SwitchRow = Gtk.Template.Child()
    indent_width: Adw.SpinRow = Gtk.Template.Child()

    _settings: Settings

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._settings = Gtk.Application.get_default().props.settings

        self._settings.bind("autosave", self.autosave_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("sort-desc", self.sort_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("spellcheck", self.spellcheck_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        # self._settings.bind("spellcheck-language", self.spellcheck_language_chooser, "value", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("autoindent", self.autoindent_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("spaces-instead-of-tabs", self.spaces_tabs_switch, "active", Gio.SettingsBindFlags.DEFAULT)
        self._settings.bind("indent-width", self.indent_width, "value", Gio.SettingsBindFlags.DEFAULT)

        # Limit indent range
        self.indent_width.set_range(0, 24)