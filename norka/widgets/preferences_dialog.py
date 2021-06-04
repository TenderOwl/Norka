# preferences_dialog.py
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

import gi

from gi.repository import Gtk, Granite, GtkSource, Gdk
from norka.services.medium import Medium
from norka.gobject_worker import GObjectWorker
from norka.services.writeas import Writeas


class PreferencesDialog(Granite.Dialog):
    __gtype_name__ = 'SettingsDialog'

    def __init__(self, transient_for, settings):
        super().__init__(transient_for=transient_for, modal=False)

        self.settings = settings
        self.set_default_size(340, 340)

        hints = Gdk.Geometry()
        hints.min_width = 340
        hints.min_height = 340
        self.set_geometry_hints(None, hints, Gdk.WindowHints.MIN_SIZE)

        self.set_border_width(5)
        self.set_deletable(False)
        self.set_title(_('Preferences'))

        self.toast = Granite.WidgetsToast(title=_("Toast"))

        indent_width = Gtk.SpinButton.new_with_range(1, 24, 1)
        indent_width.set_value(self.settings.get_int('indent-width'))
        indent_width.connect('value-changed', self.on_indent_width)

        self.sort_switch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
        self.sort_switch.set_state(self.settings.get_boolean('sort-desc'))
        self.sort_switch.connect("state-set", self.on_sort_desc)

        self.spellcheck_switch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
        self.spellcheck_switch.set_state(self.settings.get_boolean('spellcheck'))
        self.spellcheck_switch.connect("state-set", self.on_spellcheck)

        self.autosave_switch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
        self.autosave_switch.set_state(self.settings.get_boolean('autosave'))
        self.autosave_switch.connect("state-set", self.on_autosave)

        self.autoindent_switch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
        self.autoindent_switch.set_state(self.settings.get_boolean('autoindent'))
        self.autoindent_switch.connect("state-set", self.on_autoindent)

        self.spaces_tabs_switch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
        self.spaces_tabs_switch.set_state(self.settings.get_boolean('spaces-instead-of-tabs'))
        self.spaces_tabs_switch.connect("state-set", self.on_spaces_tabs)

        general_grid = Gtk.Grid(column_spacing=12, row_spacing=6)

        general_grid.attach(Granite.HeaderLabel(_("General")), 0, 0, 3, 1)
        general_grid.attach(Gtk.Label(_("Save files when changed:"), halign=Gtk.Align.END), 0, 1, 1, 1)
        general_grid.attach(self.autosave_switch, 1, 1, 1, 1)
        general_grid.attach(Gtk.Label(_("Sort documents backwards:"), halign=Gtk.Align.END), 0, 2, 1, 1)
        general_grid.attach(self.sort_switch, 1, 2, 1, 1)
        general_grid.attach(Gtk.Label(_("Spell checking:"), halign=Gtk.Align.END), 0, 3, 1, 1)
        general_grid.attach(self.spellcheck_switch, 1, 3, 1, 1)

        general_grid.attach(Granite.HeaderLabel(_("Tabs")), 0, 4, 3, 1)
        general_grid.attach(Gtk.Label(_("Automatic indentation:"), halign=Gtk.Align.END), 0, 5, 1, 1)
        general_grid.attach(self.autoindent_switch, 1, 5, 1, 1)
        general_grid.attach(Gtk.Label(_("Insert spaces instead of tabs:"), halign=Gtk.Align.END), 0, 6, 1, 1)
        general_grid.attach(self.spaces_tabs_switch, 1, 6, 1, 1)
        general_grid.attach(Gtk.Label(_("Tab width:"), halign=Gtk.Align.END), 0, 7, 1, 1)
        general_grid.attach(indent_width, 1, 7, 2, 1)

        # Interface grid
        interface_grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)

        self.dark_theme_switch = Gtk.Switch(halign=Gtk.Align.START, valign=Gtk.Align.CENTER)
        self.dark_theme_switch.set_state(self.settings.get_boolean('prefer-dark-theme'))
        self.dark_theme_switch.connect("state-set", self.on_dark_theme)

        style_chooser = GtkSource.StyleSchemeChooserWidget()
        style_chooser.connect('notify::style-scheme', self.on_scheme_changed)
        scrolled.add(style_chooser)

        scheme = GtkSource.StyleSchemeManager().get_scheme(
            self.settings.get_string('stylescheme')
        )
        if not scheme:
            scheme = GtkSource.StyleSchemeManager().get_scheme("classic")

        style_chooser.set_style_scheme(scheme)

        interface_grid.attach(Granite.HeaderLabel(_("Appearance")), 0, 0, 3, 1)
        interface_grid.attach(Gtk.Label(_("Prefer dark theme:"), halign=Gtk.Align.END), 0, 1, 2, 1)
        interface_grid.attach(self.dark_theme_switch, 2, 1, 1, 1)
        interface_grid.attach(Granite.HeaderLabel(_("Styles")), 0, 2, 3, 1)
        interface_grid.attach(scrolled, 0, 3, 3, 1)

        # Export grid
        export_grid = Gtk.Grid(column_spacing=12, row_spacing=6)

        self.render_medium(export_grid)
        self.render_writeas(export_grid)

        # Main Stack
        main_stack = Gtk.Stack(margin=6, margin_bottom=18, margin_top=8)
        main_stack.add_titled(general_grid, "behavior", _("Behavior"))
        main_stack.add_titled(interface_grid, "interface", _("Interface"))
        main_stack.add_titled(export_grid, "export", _("Export"))

        main_stackswitcher = Gtk.StackSwitcher()
        main_stackswitcher.set_stack(main_stack)
        main_stackswitcher.set_halign(Gtk.Align.CENTER)

        main_grid = Gtk.Grid()
        main_grid.attach(main_stackswitcher, 0, 0, 1, 1)
        main_grid.attach(main_stack, 0, 1, 1, 1)

        self.overlay = Gtk.Overlay()
        self.overlay.add(main_grid)
        self.overlay.add_overlay(self.toast)
        self.get_content_area().add(self.overlay)

        close_button = Gtk.Button(label=_("Close"))
        close_button.connect('clicked', self.on_close_activated)
        self.add_action_widget(close_button, 0)

    def render_medium(self, content_grid):
        self.medium_token = Gtk.Entry(hexpand=True, placeholder_text=_("Token"))
        self.medium_token.set_text(self.settings.get_string('medium-personal-token'))
        self.medium_token.connect("changed", self.on_medium_token)

        self.medium_link = Gtk.LinkButton("https://medium.com/me/settings")
        self.medium_link.set_label(_("Create Integration token and copy it here"))

        content_grid.attach(Granite.HeaderLabel("Medium.com"), 0, 0, 3, 1)
        content_grid.attach(Gtk.Label(_("Personal Token:"), halign=Gtk.Align.END), 0, 1, 1, 1)
        content_grid.attach(self.medium_token, 1, 1, 2, 1)
        content_grid.attach(self.medium_link, 0, 2, 3, 1)

    def render_writeas(self, content_grid):
        self.writeas_login = Gtk.Entry(hexpand=True, placeholder_text=_("Login"))
        self.writeas_password = Gtk.Entry(hexpand=True, placeholder_text=_("Password"), visibility=False)
        self.writeas_login_button = Gtk.Button(label=_("Login"))
        self.writeas_login_button.connect("clicked", self.on_writeas_login)
        self.writeas_logout_button = Gtk.Button(label=_("Logout"), hexpand=True)
        self.writeas_logout_button.connect("clicked", self.on_writeas_logout)

        content_grid.attach(Granite.HeaderLabel("Write.as"), 0, 3, 3, 1)

        self.writeas_login_revealer = Gtk.Revealer()
        self.writeas_login_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        login_grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        login_grid.attach(Gtk.Label(_("Login:"), halign=Gtk.Align.END), 0, 0, 1, 1)
        login_grid.attach(self.writeas_login, 1, 0, 2, 1)
        login_grid.attach(Gtk.Label(_("Password:"), halign=Gtk.Align.END), 0, 1, 1, 1)
        login_grid.attach(self.writeas_password, 1, 1, 2, 1)
        login_grid.attach(self.writeas_login_button, 0, 2, 3, 1)
        self.writeas_login_revealer.add(login_grid)

        self.writeas_logout_revealer = Gtk.Revealer()
        self.writeas_logout_revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
        logout_grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        logout_grid.attach(self.writeas_logout_button, 0, 0, 3, 1)
        self.writeas_logout_revealer.add(logout_grid)

        content_grid.attach(self.writeas_login_revealer, 0, 4, 3, 1)
        content_grid.attach(self.writeas_logout_revealer, 0, 4, 3, 1)

        self.writeas_reveal()

        self.settings.connect("changed", self.on_settings_changed)

    def on_spellcheck(self, sender: Gtk.Widget, state):
        self.settings.set_boolean("spellcheck", state)
        return False

    def on_sort_desc(self, sender: Gtk.Widget, state):
        self.settings.set_boolean("sort-desc", state)
        return False

    def on_autosave(self, sender: Gtk.Widget, state):
        self.settings.set_boolean("autosave", state)
        return False

    def on_close_activated(self, sender: Gtk.Widget):
        self.destroy()

    def on_dark_theme(self, sender, state):
        self.settings.set_boolean('prefer-dark-theme', state)

    def on_scheme_changed(self, style_chooser, event):
        self.settings.set_string('stylescheme', style_chooser.get_style_scheme().get_id())

    def on_autoindent(self, sender, state):
        self.settings.set_boolean('autoindent', state)

    def on_spaces_tabs(self, sender, state):
        self.settings.set_boolean('spaces-instead-of-tabs', state)

    def on_indent_width(self, sender: Gtk.SpinButton) -> None:
        self.settings.set_int('indent-width', sender.get_value_as_int())

    def on_medium_token(self, sender: Gtk.Entry) -> None:
        token = sender.get_text().strip()
        self.settings.set_string("medium-personal-token", token)
        if token:
            sender.set_sensitive(False)
            medium_client = Medium(access_token=token)
            GObjectWorker.call(medium_client.get_user, callback=self.on_medium_callback)
        else:
            self.settings.set_string("medium-user-id", "")

    def on_medium_callback(self, result):
        self.medium_token.set_sensitive(True)
        if result:
            self.toast.set_title(f"Token accepted, {result['name']}!")
            self.settings.set_string("medium-user-id", result['id'])
            self.toast.send_notification()
        else:
            self.on_medium_errorback()

    def on_medium_errorback(self, error=None):
        self.medium_token.set_sensitive(True)
        self.toast.set_title(_("Something goes wrong!"))
        self.toast.send_notification()
        self.settings.set_string("medium-user-id", "")

    def on_writeas_login(self, button: Gtk.Button):
        """Login to write.as and save token on success
        """
        # Disable widgets while login
        self.writeas_login.set_sensitive(False)
        self.writeas_password.set_sensitive(False)
        self.writeas_login_button.set_sensitive(False)

        GObjectWorker.call(Writeas().login,
                           (self.writeas_login.get_text(), self.writeas_password.get_text()),
                           self.on_writeas_callback)

    def on_writeas_logout(self, button: Gtk.Button):
        """Clear writeas access token settings
        """
        self.toast.send_notification()
        self.settings.set_string("writeas-access-token", "")

    def writeas_reveal(self):
        """Toggle writeas revealers state
        """
        # Maybe I should rewrite it with bind_property
        if self.settings.get_string("writeas-access-token"):
            self.writeas_login_revealer.set_reveal_child(False)
            self.writeas_logout_revealer.set_reveal_child(True)
            self.writeas_login_revealer.set_visible(False)
            self.writeas_logout_revealer.set_visible(True)
        else:
            self.writeas_login_revealer.set_reveal_child(True)
            self.writeas_logout_revealer.set_reveal_child(False)
            self.writeas_login_revealer.set_visible(True)
            self.writeas_logout_revealer.set_visible(False)

    def on_writeas_callback(self, result):
        data, error = result
        self.toast.set_default_action(None)
        if error:
            self.toast.set_title(_("Login failed."))
            self.toast.send_notification()

        if data and "access_token" in data:
            self.settings.set_string("writeas-access-token", data["access_token"])
            self.toast.set_title(_("Logged as {}.").format(data['user']['username']))
            self.toast.send_notification()

        # Enable widgets while login
        self.writeas_login.set_sensitive(True)
        self.writeas_password.set_sensitive(True)
        self.writeas_login_button.set_sensitive(True)

    def on_settings_changed(self, settings, key):
        if key == "writeas-access-token":
            self.writeas_reveal()
