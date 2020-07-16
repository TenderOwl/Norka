# menu_export.py
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


class MenuExport(Gtk.Popover):
    def __init__(self, settings):
        super().__init__()
        self.set_relative_to(None)

        self.settings = settings

        self.export_file = Gtk.ModelButton()
        self.export_file.get_child().destroy()
        self.export_file.add(Granite.AccelLabel(label="Export to file", accel_string='<Control><Shift>s'))
        self.export_file.set_action_name("document.export")

        self.export_medium = Gtk.ModelButton()
        self.export_medium.get_child().destroy()
        self.export_medium.add(Granite.AccelLabel(label="To Medium"))
        self.export_medium.set_action_name("document.export-medium")

        self.export_writeas = Gtk.ModelButton()
        self.export_writeas.get_child().destroy()
        self.export_writeas.add(Granite.AccelLabel(label="To Write.as"))
        self.export_writeas.set_action_name("document.export-writeas")

        menu_grid = Gtk.Grid(margin_bottom=3, margin_top=3, orientation=Gtk.Orientation.VERTICAL, width_request=200)

        menu_grid.attach(self.export_file, 0, 0, 3, 1)
        menu_grid.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), 0, 1, 3, 1)
        menu_grid.attach(self.export_medium, 0, 2, 3, 1)
        menu_grid.attach(self.export_writeas, 0, 3, 3, 1)

        self.add(menu_grid)

        menu_grid.show_all()
