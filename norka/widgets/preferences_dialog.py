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

from gi.repository import Gtk, Granite


class PreferencesDialog(Gtk.Dialog):
    __gtype_name__ = 'SettingsDialog'

    def __init__(self, transient_for, settings):
        super().__init__(transient_for=transient_for, modal=False)

        self.settings = settings

        self.set_border_width(5)
        self.set_deletable(False)
        self.set_resizable(False)
        self.set_title('Preferences')

        self.spellcheck_switch = Gtk.Switch()
        self.spellcheck_switch.set_state(self.settings.get_boolean('spellcheck'))
        self.spellcheck_switch.connect("state-set", self.on_spellcheck)

        self.autosave_switch = Gtk.Switch()
        self.autosave_switch.set_state(self.settings.get_boolean('autosave'))
        self.autosave_switch.connect("state-set", self.on_autosave)

        general_grid = Gtk.Grid(column_spacing=12, row_spacing=6)
        general_grid.attach(Granite.HeaderLabel("General"), 0, 0, 2, 1)
        general_grid.attach(Gtk.Label("Save files when changed:", halign=Gtk.Align.END), 0, 1, 1, 1)
        general_grid.attach(self.autosave_switch, 1, 1, 1, 1)
        general_grid.attach(Gtk.Label("Spell checking:", halign=Gtk.Align.END), 0, 2, 1, 1)
        general_grid.attach(self.spellcheck_switch, 1, 2, 1, 1)

        main_stack = Gtk.Stack(margin=6, margin_bottom=18, margin_top=8)
        main_stack.add_titled(general_grid, "behavior", "Behavior")

        # main_stackswitcher = Gtk.StackSwitcher()
        # main_stackswitcher.set_stack(main_stack)
        # main_stackswitcher.set_halign(Gtk.Align.CENTER)

        main_grid = Gtk.Grid()
        # main_grid.attach(main_stackswitcher, 0, 0, 1, 1)
        main_grid.attach(main_stack, 0, 0, 1, 1)

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
