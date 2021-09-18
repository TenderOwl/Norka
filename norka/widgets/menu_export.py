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

from gettext import gettext as _

from gi.repository import Gtk, Granite, Handy

from norka.define import RESOURCE_PREFIX


class MenuExport(Gtk.Popover):
    def __init__(self, settings):
        super().__init__()
        self.set_constrain_to(Gtk.PopoverConstraint.NONE)

        self.settings = settings

        self.export_plain = Gtk.Button(
            label=_("Text"),
            action_name="document.export",
            tooltip_text=_("Export document to plain text file"),
            relief=Gtk.ReliefStyle.NONE,
            always_show_image=True,
            image_position=Gtk.PositionType.TOP)
        self.export_plain.set_image(
            Gtk.Image.new_from_resource(f"{RESOURCE_PREFIX}/icons/text.svg"))

        self.export_markdown = Gtk.Button(
            label=_("Markdown"),
            action_name="document.export-markdown",
            tooltip_markup=Granite.markup_accel_tooltip(
                ("<Control><Shift>s",), _("Export document to markdown")),
            relief=Gtk.ReliefStyle.NONE,
            always_show_image=True,
            image_position=Gtk.PositionType.TOP)
        self.export_markdown.set_image(
            Gtk.Image.new_from_resource(f"{RESOURCE_PREFIX}/icons/text-markdown.svg"))

        self.export_html = Gtk.Button(
            _("Html"),
            action_name="document.export-html",
            tooltip_text=_("Export document to HTML"),
            relief=Gtk.ReliefStyle.NONE,
            always_show_image=True,
            image_position=Gtk.PositionType.TOP)
        self.export_html.set_tooltip_text(_("Export document to HTML"))
        self.export_html.set_image(
            Gtk.Image.new_from_resource(f"{RESOURCE_PREFIX}/icons/text-html.svg"))

        self.export_pdf = Gtk.Button(
            _("Pdf"),
            action_name="document.export-pdf",
            tooltip_text=_("Export document to PDF"),
            relief=Gtk.ReliefStyle.NONE,
            always_show_image=True,
            image_position=Gtk.PositionType.TOP)
        self.export_pdf.set_tooltip_text(_("Export document to PDF"))
        self.export_pdf.set_image(
            Gtk.Image.new_from_resource(f"{RESOURCE_PREFIX}/icons/application-pdf.svg"))

        self.export_docx = Gtk.Button(
            _("Docx"),
            action_name="document.export-docx",
            tooltip_text=_("Export document to Docx"),
            relief=Gtk.ReliefStyle.NONE,
            always_show_image=True,
            image_position=Gtk.PositionType.TOP)
        self.export_docx.set_tooltip_text(_("Export document to Docx"))
        self.export_docx.set_image(
            Gtk.Image.new_from_resource(f"{RESOURCE_PREFIX}/icons/application-msword.svg"))

        export_grid_1 = Gtk.Grid()
        export_grid_1.attach(self.export_plain, 0, 1, 1, 1)
        export_grid_1.attach(self.export_markdown, 1, 1, 1, 1)
        export_grid_1.attach(self.export_html, 2, 1, 1, 1)

        export_grid_2 = Gtk.Grid()
        export_grid_2.attach(self.export_pdf, 0, 1, 1, 1)
        export_grid_2.attach(self.export_docx, 1, 1, 1, 1)

        self.carousel = Handy.Carousel()
        self.carousel_indicator = Handy.CarouselIndicatorLines(carousel=self.carousel)
        self.carousel.insert(export_grid_1, 0)
        self.carousel.insert(export_grid_2, 1)

        self.export_file = Gtk.ModelButton()
        self.export_file.get_child().destroy()
        self.export_file.add(Granite.AccelLabel(label=_("Export to file"), accel_string='<Control><Shift>s'))
        self.export_file.set_action_name("document.export")

        self.export_medium = Gtk.ModelButton()
        self.export_medium.get_child().destroy()
        self.export_medium.add(Granite.AccelLabel(label=_("To Medium")))
        self.export_medium.set_action_name("document.export-medium")

        self.export_writeas = Gtk.ModelButton()
        self.export_writeas.get_child().destroy()
        self.export_writeas.add(Granite.AccelLabel(label=_("To Write.as")))
        self.export_writeas.set_action_name("document.export-writeas")

        menu_grid = Gtk.Grid(margin_bottom=3, margin_top=3, orientation=Gtk.Orientation.VERTICAL, width_request=200)
        menu_grid.attach(Granite.HeaderLabel(_("Files"), margin_left=12, margin_right=12), 0, 0, 3, 1)
        menu_grid.attach(self.carousel, 0, 1, 3, 1)
        menu_grid.attach(self.carousel_indicator, 0, 2, 3, 1)

        menu_grid.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, margin_top=12), 0, 2, 3, 1)
        menu_grid.attach(Granite.HeaderLabel(_("Internet"), margin_left=12, margin_right=12), 0, 3, 3, 1)
        menu_grid.attach(self.export_medium, 0, 4, 3, 1)
        menu_grid.attach(self.export_writeas, 0, 5, 3, 1)

        self.add(menu_grid)

        menu_grid.show_all()
