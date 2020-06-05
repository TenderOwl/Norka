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

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Granite', '1.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, Granite, GtkSource


class PreferencesDialog(Gtk.Dialog):
    __gtype_name__ = 'SettingsDialog'

    def __init__(self, transient_for, settings):
        super().__init__(transient_for=transient_for, modal=False)

        self.settings = settings
        self.set_default_size(340, 300)

        self.set_border_width(5)
        self.set_deletable(False)
        self.set_title('Preferences')

        indent_width = Gtk.SpinButton.new_with_range(1, 24, 1)
        indent_width.set_value(self.settings.get_int('indent-width'))
        indent_width.connect('change-value', self.on_indent_width)

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

        general_grid.attach(Granite.HeaderLabel("General"), 0, 0, 3, 1)
        general_grid.attach(Gtk.Label("Save files when changed:", halign=Gtk.Align.END), 0, 1, 1, 1)
        general_grid.attach(self.autosave_switch, 1, 1, 1, 1)
        general_grid.attach(Gtk.Label("Spell checking:", halign=Gtk.Align.END), 0, 2, 1, 1)
        general_grid.attach(self.spellcheck_switch, 1, 2, 1, 1)

        general_grid.attach(Granite.HeaderLabel("Tabs"), 0, 3, 3, 1)
        general_grid.attach(Gtk.Label("Automatic indentation:", halign=Gtk.Align.END), 0, 4, 1, 1)
        general_grid.attach(self.autoindent_switch, 1, 4, 1, 1)
        general_grid.attach(Gtk.Label("Insert spaces instead of tabs:", halign=Gtk.Align.END), 0, 5, 1, 1)
        general_grid.attach(self.spaces_tabs_switch, 1, 5, 1, 1)
        general_grid.attach(Gtk.Label("Tab width:", halign=Gtk.Align.END), 0, 6, 1, 1)
        general_grid.attach(indent_width, 1, 6, 2, 1)

        interface_grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        scrolled = Gtk.ScrolledWindow(hexpand=True, vexpand=True)
        style_chooser = GtkSource.StyleSchemeChooserWidget()
        style_chooser.connect('notify::style-scheme', self.on_scheme_changed)
        scrolled.add(style_chooser)

        scheme = GtkSource.StyleSchemeManager().get_scheme(
            self.settings.get_string('stylescheme')
        )
        style_chooser.set_style_scheme(scheme)

        interface_grid.attach(Granite.HeaderLabel("Styles"), 0, 0, 2, 1)
        interface_grid.attach(scrolled, 0, 2, 1, 1)

        main_stack = Gtk.Stack(margin=6, margin_bottom=18, margin_top=8)
        main_stack.add_titled(general_grid, "behavior", "Behavior")
        main_stack.add_titled(interface_grid, "interface", "Interface")

        main_stackswitcher = Gtk.StackSwitcher()
        main_stackswitcher.set_stack(main_stack)
        main_stackswitcher.set_halign(Gtk.Align.CENTER)

        main_grid = Gtk.Grid()
        main_grid.attach(main_stackswitcher, 0, 0, 1, 1)
        main_grid.attach(main_stack, 0, 1, 1, 1)

        self.get_content_area().add(main_grid)

        close_button = Gtk.Button(label="Close")
        close_button.connect('clicked', self.on_close_activated)
        self.add_action_widget(close_button, 0)

    def on_spellcheck(self, sender: Gtk.Widget, state):
        self.settings.set_boolean("spellcheck", state)
        return False

    def on_autosave(self, sender: Gtk.Widget, state):
        self.settings.set_boolean("autosave", state)
        return False

    def on_close_activated(self, sender: Gtk.Widget):
        self.destroy()

    def on_scheme_changed(self, style_chooser, event):
        self.settings.set_string('stylescheme', style_chooser.get_style_scheme().get_id())

    def on_autoindent(self, sender, state):
        self.settings.set_boolean('autoindent', state)

    def on_spaces_tabs(self, sender, state):
        self.settings.set_boolean('spaces-instead-of-tabs', state)

    def on_indent_width(self, sender, value):
        self.settings.set_int('indent-width', value)
