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
import os
import sys
from gettext import gettext as _
from typing import List

from gi.repository import Gtk, Gio, Gdk, Granite, GLib, Handy

from norka.define import APP_ID, RESOURCE_PREFIX, STORAGE_NAME, APP_TITLE
from norka.services.logger import Logger
from norka.services.settings import Settings
from norka.services.storage import Storage
from norka.widgets.about_dialog import AboutDialog
from norka.widgets.format_shortcuts_dialog import FormatShortcutsWindow
from norka.widgets.preferences_dialog import PreferencesDialog
from norka.window import NorkaWindow


class Application(Gtk.Application):
    __gtype_name__ = 'NorkaApplication'

    granite_settings: Granite.Settings
    gtk_settings: Gtk.Settings

    def __init__(self, version: str = None):
        super().__init__(application_id=APP_ID,
                         flags=Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)

        Handy.init()

        self.add_main_option('new', ord("n"),
                             GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             _('Open new document on start.'))

        self.version = version

        # Init GSettings
        self.settings = Settings.new()

        self.init_style()
        self.window: NorkaWindow = None

        # Init storage location and SQL structure
        self.base_path = os.path.join(GLib.get_user_data_dir(), APP_TITLE)
        storage_path = self.settings.get_string("storage-path")
        if not storage_path:
            storage_path = os.path.join(self.base_path, STORAGE_NAME)
            self.settings.set_string("storage-path", storage_path)

        self.storage = Storage(storage_path)
        try:
            self.storage.init()
        except Exception as e:
            sys.exit(e)

        quit_action = Gio.SimpleAction.new(name="quit", parameter_type=None)
        quit_action.connect("activate", self.on_quit)
        self.add_action(quit_action)
        self.set_accels_for_action('app.quit', ('<Control>q',))

        about_action = Gio.SimpleAction.new(name="about", parameter_type=None)
        about_action.connect("activate", self.on_about)
        self.add_action(about_action)

        preferences_action = Gio.SimpleAction.new(name="preferences", parameter_type=None)
        preferences_action.connect("activate", self.on_preferences)
        self.add_action(preferences_action)
        self.set_accels_for_action('app.preferences', ('<Control>comma',))

        shortcuts_action = Gio.SimpleAction.new(name="shortcuts", parameter_type=None)
        shortcuts_action.connect("activate", self.on_shortcuts)
        self.add_action(shortcuts_action)

        format_shortcuts_action = Gio.SimpleAction.new(name="format_shortcuts", parameter_type=None)
        format_shortcuts_action.connect("activate", self.on_format_shortcuts)
        self.add_action(format_shortcuts_action)

    def init_style(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_resource(f"{RESOURCE_PREFIX}/css/application.css")
        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        if self.settings.get_boolean('prefer-dark-theme'):
            Gtk.Settings.get_default().props.gtk_application_prefer_dark_theme = True

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # builder = Gtk.Builder.new_from_resource(f"{RESOURCE_PREFIX}/ui/app_menu.xml")
        # self.set_app_menu(builder.get_object('app-menu'))
        self.settings.connect("changed", self.on_settings_changed)

    def do_activate(self):
        """Activates the application.

        """
        self.granite_settings = Granite.Settings.get_default()
        self.gtk_settings = Gtk.Settings.get_default()

        # Setup default theme mode
        if self.settings.get_boolean('prefer-dark-theme'):
            self.gtk_settings.props.gtk_application_prefer_dark_theme = True
        else:
            # Then, we check if the user's preference is for the dark style and set it if it is
            self.gtk_settings.props.gtk_application_prefer_dark_theme = \
                self.granite_settings.props.prefers_color_scheme == Granite.SettingsColorScheme.DARK

        # Finally, we listen to changes in Granite.Settings and update our app if the user changes their preference
        self.granite_settings.connect("notify::prefers-color-scheme",
                                      self.color_scheme_changed)

        self.window = self.props.active_window
        if not self.window:
            self.window = NorkaWindow(application=self, settings=self.settings, storage=self.storage)
        self.window.present()

    def do_open(self, files: List[Gio.File], n_files: int, hint: str):
        """Opens the given files.

        :param files: an array of Gio.Files to open
        :param n_files: number of files in command line args
        :param hint: a hint (or “”), but never None
        """
        print(f'Openin {n_files} files')
        if n_files and not self.window:
            self.do_activate()

        doc_id = None
        for gfile in files:
            path = gfile.get_path()
            if not path:
                continue
            doc_id = self.window.import_document(file_path=path)

        # Open last imported file
        if doc_id:
            self.window.document_activate(doc_id)

    def do_handle_local_options(self, options):
        self.activate()
        options = options.end().unpack()
        if 'new' in options:
            new_arg_value = options['new']
            # print('new document flag')
            if new_arg_value and not self.window.is_document_editing:
                self.window.on_document_create_activated(title=new_arg_value)
            return 1
        return -1

    def on_settings_changed(self, settings, key):
        Logger.debug(f'SETTINGS: %s changed', key)
        if key == "autosave":
            self.window.autosave = settings.get_boolean(key)
        if key == "spellcheck":
            self.window.toggle_spellcheck(settings.get_boolean(key))
        if key == "spellcheck-language":
            self.window.set_spellcheck_language(settings.get_string(key))
        if key == 'stylescheme':
            self.window.set_style_scheme(settings.get_string(key))
        if key == 'autoindent':
            self.window.set_autoindent(settings.get_boolean('autoindent'))
        if key == 'spaces-instead-of-tabs':
            self.window.set_tabs_spaces(settings.get_boolean('spaces-instead-of-tabs'))
        if key == 'indent-width':
            self.window.set_indent_width(settings.get_int('indent-width'))
        if key == 'font':
            self.window.editor.update_font(settings.get_string('font'))
        if key == 'prefer-dark-theme':
            Gtk.Settings.get_default().props.gtk_application_prefer_dark_theme = \
                settings.get_boolean('prefer-dark-theme')

    def on_preferences(self, sender: Gtk.Widget = None, event=None) -> None:
        preferences_dialog = PreferencesDialog(transient_for=self.window, settings=self.settings)
        preferences_dialog.show_all()
        preferences_dialog.present()

    def on_quit(self, action, param):
        self.props.active_window.on_window_delete_event()
        self.settings.sync()
        self.quit()

    def on_about(self, action, param):
        about_dialog = AboutDialog(version=self.version, transient_for=self.window, modal=True, )
        about_dialog.present()

    def color_scheme_changed(self, _old, _new):
        dark_mode = self.settings.get_boolean('prefer-dark-theme')
        if not dark_mode:
            self.gtk_settings.props.gtk_application_prefer_dark_theme = \
                self.granite_settings.props.prefers_color_scheme == Granite.SettingsColorScheme.DARK

    def on_shortcuts(self, action, param):
        builder = Gtk.Builder.new_from_resource(f"{RESOURCE_PREFIX}/ui/shortcuts.ui")
        dialog = builder.get_object("shortcuts")
        dialog.set_transient_for(self.window)
        dialog.show()

    def on_format_shortcuts(self, action, param):
        dialog = FormatShortcutsWindow()
        dialog.set_transient_for(self.window)
        dialog.show()


def main(version: str = None):
    app = Application(version=version)
    app.run(sys.argv)


if __name__ == '__main__':
    main()
