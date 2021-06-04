# format_shortcuts_dialog.py
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

from gi.repository import Gtk, Granite


class FormatShortcutsDialog(Granite.Dialog):

    def __init__(self):
        super().__init__(title=_('Markup Help'))
        self.set_default_size(300, 340)

        h1_label = Gtk.Label(label=f'{self.span_text("#")} {_("Header")} 1',
                             halign=Gtk.Align.START,
                             use_markup=True)
        h1_keys = Granite.AccelLabel(accel_string='<Control>1')

        h2_label = Gtk.Label(label=f'{self.span_text("##")} {_("Header")} 2',
                             halign=Gtk.Align.START,
                             use_markup=True)
        h2_keys = Granite.AccelLabel(accel_string='<Control>2')

        h3_label = Gtk.Label(label=f'{self.span_text("###")} {_("Header")} 3',
                             halign=Gtk.Align.START,
                             use_markup=True)
        h3_keys = Granite.AccelLabel(accel_string='<Control>3')

        bold_label = Gtk.Label(label=f'{self.span_text("**")}{_("Bold")}{self.span_text("**")}',
                               halign=Gtk.Align.START,
                               use_markup=True)
        bold_keys = Granite.AccelLabel(accel_string='<Control>b')

        italic_label = Gtk.Label(label=f'{self.span_text("_")}{_("Italic")}{self.span_text("_")}',
                                 halign=Gtk.Align.START,
                                 use_markup=True)
        italic_keys = Granite.AccelLabel(accel_string='<Control>i')

        link_label = Gtk.Label(label=f'{self.span_text("[")}{_("Link title")}{self.span_text("]")}'
                                     f'{self.span_text("(")}{_("URL")}{self.span_text(")")}',
                               halign=Gtk.Align.START,
                               use_markup=True)
        link_keys = Granite.AccelLabel(accel_string='<Control>k')

        image_link_label = Gtk.Label(label=f'{self.span_text("![")}{_("Image title")}{self.span_text("]")}'
                                           f'{self.span_text("(")}{_("URL")}{self.span_text(")")}',
                                     halign=Gtk.Align.START,
                                     use_markup=True)
        image_link_keys = Granite.AccelLabel(accel_string='<Control><Shift>k')

        list_label = Gtk.Label(label=f'{self.span_text("-")} {_("List")}',
                               halign=Gtk.Align.START,
                               use_markup=True)
        list_keys = Granite.AccelLabel(accel_string='<Control>l')

        ordered_list_label = Gtk.Label(label=f'{self.span_text("1.")} {_("Ordered list")}',
                                       halign=Gtk.Align.START,
                                       use_markup=True)
        ordered_list_keys = Granite.AccelLabel(accel_string='<Control><Shift>l')

        quote_label = Gtk.Label(label=f'{self.span_text(">")} {_("Quote")}',
                                halign=Gtk.Align.START,
                                use_markup=True)
        quote_keys = Granite.AccelLabel(accel_string='<Control><Shift>j')

        code_label = Gtk.Label(label=f'{self.span_text("`")}{_("Inline code")}{self.span_text("`")}',
                               halign=Gtk.Align.START,
                               use_markup=True)
        code_keys = Granite.AccelLabel(accel_string='<Control><Shift>c')

        code_block_label = Gtk.Label(label=f'{self.span_text("```")}{_("Code block")}{self.span_text("```")}',
                                     halign=Gtk.Align.START,
                                     use_markup=True)
        code_block_keys = Granite.AccelLabel(accel_string='<Control><Alt>c')

        grid = Gtk.Grid(column_spacing=6, row_spacing=6,
                        margin_start=12,
                        margin_end=12,
                        margin_top=12,
                        margin_bottom=12, )

        grid.attach(h1_label, 1, 0, 1, 1)
        grid.attach(h1_keys, 2, 0, 1, 1)
        grid.attach(h2_label, 1, 1, 1, 1)
        grid.attach(h2_keys, 2, 1, 1, 1)
        grid.attach(h3_label, 1, 2, 1, 1)
        grid.attach(h3_keys, 2, 2, 1, 1)

        grid.attach(self.make_sep(), 1, 3, 3, 1)

        grid.attach(bold_label, 1, 4, 1, 1)
        grid.attach(bold_keys, 2, 4, 1, 1)
        grid.attach(italic_label, 1, 5, 1, 1)
        grid.attach(italic_keys, 2, 5, 1, 1)
        grid.attach(link_label, 1, 6, 1, 1)
        grid.attach(link_keys, 2, 6, 1, 1)
        grid.attach(image_link_label, 1, 7, 1, 1)
        grid.attach(image_link_keys, 2, 7, 1, 1)

        grid.attach(self.make_sep(), 1, 8, 3, 1)

        grid.attach(list_label, 1, 9, 1, 1)
        grid.attach(list_keys, 2, 9, 1, 1)
        grid.attach(ordered_list_label, 1, 10, 1, 1)
        grid.attach(ordered_list_keys, 2, 10, 1, 1)
        grid.attach(quote_label, 1, 11, 1, 1)
        grid.attach(quote_keys, 2, 11, 1, 1)

        grid.attach(self.make_sep(), 1, 13, 3, 1)

        grid.attach(code_label, 1, 14, 1, 1)
        grid.attach(code_keys, 2, 14, 1, 1)
        grid.attach(code_block_label, 1, 15, 1, 1)
        grid.attach(code_block_keys, 2, 15, 1, 1)

        self.get_content_area().add(grid)

        self.show_all()

    @staticmethod
    def make_sep():
        return Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL,
                             margin_top=12,
                             margin_bottom=12)

    @staticmethod
    def span_text(text):
        return f'<span alpha="40%" weight="bold">{text}</span>'
