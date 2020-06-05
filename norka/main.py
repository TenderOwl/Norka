# main.py
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

import sys

import gi

from norka.widgets.preferences_dialog import PreferencesDialog

gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
gi.require_version('GtkSpell', '3.0')

from gi.repository import Gtk, Gio, Gdk

from norka.define import APP_ID
from norka.services.logger import Logger
from norka.services.settings import Settings
from norka.services.storage import storage
from norka.widgets.about_dialog import AboutDialog
from norka.window import NorkaWindow


class Application(Gtk.Application):
    __gtype_name__ = 'NorkaApplication'

    def __init__(self, version: str = None):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        # Init GSettings
        self.settings = Settings.new()

        self.init_style()
        self.window = None

        # Init storage location and SQL structure
        try:
            storage.init()
        except Exception as e:
            sys.exit(e)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        self.set_accels_for_action('app.quit', ('<Control>q',))

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("preferences", None)
        action.connect("activate", self.on_preferences)
        self.add_action(action)
        self.set_accels_for_action('app.preferences', ('<Control>comma',))

    def init_style(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource('/com/github/tenderowl/norka/css/application.css')
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self.settings.connect("changed", self.on_settings_changed)

    def do_activate(self):
        self.window = self.props.active_window
        if not self.window:
            self.window = NorkaWindow(application=self, settings=self.settings)
        self.window.present()

    def on_settings_changed(self, settings, key):
        Logger.debug(f'SETTINGS: %s changed', key)
        if key == "spellcheck":
            self.window.toggle_spellcheck(settings.get_boolean(key))
        elif key == 'stylescheme':
            self.window.set_style_scheme(settings.get_string(key))

    def on_preferences(self, sender: Gtk.Widget = None, event=None) -> None:
        preferences_dialog = PreferencesDialog(transient_for=self.window, settings=self.settings)
        preferences_dialog.show_all()
        preferences_dialog.present()

    def on_quit(self, action, param):
        self.props.active_window.on_window_delete_event()
        self.settings.sync()
        self.quit()

    def on_about(self, action, param):
        about_dialog = AboutDialog(transient_for=self.window, modal=True)
        about_dialog.present()


def main(version: str = None):
    app = Application(version=version)
    app.run(sys.argv)


if __name__ == '__main__':
    main()
