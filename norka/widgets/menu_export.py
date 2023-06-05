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
        # self.set_constrain_to(Gtk.PopoverConstraint.NONE)

        self.settings = settings

        self.export_plain = Gtk.Button(
            label=_("Text"),
            action_name="document.export",
            tooltip_text=_("Export document to plain text file"),
            relief=Gtk.ReliefStyle.NONE,
            always_show_image=True,
            image_position=Gtk.PositionType.TOP)
        self.export_plain.set_image(Gtk.Image.new_from_resource(f"{RESOURCE_PREFIX}/icons/text.svg"))

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
            label=_("Html"),
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
            image_position=Gtk.PositionType.TOP, )
        self.export_pdf.set_tooltip_text(_("Export document to PDF"))
        self.export_pdf.set_image(
            Gtk.Image.new_from_resource(f"{RESOURCE_PREFIX}/icons/application-pdf.svg"))

        self.export_docx = Gtk.Button(
            label=_("Docx"),
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

        self.export_file = Gtk.Button(label=_("Export to file"))
        self.export_file.set_action_name("document.export")

        self.export_medium = Gtk.Button(label=_("To Medium"))
        self.export_medium.get_style_context().add_class('flat')
        self.export_medium.set_action_name("document.export-medium")

        self.export_writeas = Gtk.Button(label=_("To Write.as"))
        self.export_writeas.get_style_context().add_class('flat')
        self.export_writeas.set_action_name("document.export-writeas")

        menu_grid = Gtk.Grid(margin_bottom=8, margin_top=8,
                             margin_start=8, margin_end=8,
                             orientation=Gtk.Orientation.VERTICAL, width_request=200)
        files_label = Gtk.Label(
            label=_("Files"),
            margin_top=8,
            margin_bottom=8,
            halign=Gtk.Align.START)
        files_label.get_style_context().add_class('title-4')
        menu_grid.attach(files_label, 0, 0, 3, 1)
        menu_grid.attach(self.carousel, 0, 1, 3, 1)
        menu_grid.attach(self.carousel_indicator, 0, 2, 3, 1)

        menu_grid.attach(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL, margin_top=12), 0, 2, 3, 1)
        internet_label = Gtk.Label(
            label=_("Internet"),
            margin_top=8,
            margin_bottom=8,
            halign=Gtk.Align.START)
        internet_label.get_style_context().add_class('title-4')
        menu_grid.attach(internet_label, 0, 3, 3, 1)
        menu_grid.attach(self.export_medium, 0, 4, 3, 1)
        menu_grid.attach(self.export_writeas, 0, 5, 3, 1)

        self.add(menu_grid)

        menu_grid.show_all()
        self.export_pdf.set_visible(False)
