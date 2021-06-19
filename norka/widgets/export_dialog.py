# export_dialog.py
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

from gi.repository import Gtk


class ExportFormat:
    PlainText = (_("Plain text"), ("*.txt",))
    Markdown = (_("Markdown"), ("*.md", "*.markdown",))
    Html = (_("HTML"), ("*.html", "*.htm"))
    Pdf = (_("PDF"), ("*.pdf",))
    Docx = (_("Docx"), ("*.docx",))


class ExportFileDialog(Gtk.FileChooserNative):
    def __init__(self, title=None, parent=None, action=None, accept_label=None, cancel_label=None):
        super().__init__()

        self.props.title = title
        self.props.transient_for = parent
        self.props.action = action
        self.props.accept_label = accept_label
        self.props.cancel_label = cancel_label

        self.set_do_overwrite_confirmation(True)

    def set_format(self, export_format: ExportFormat):
        file_filter = Gtk.FileFilter()
        file_filter.set_name(export_format[0])
        for pattern in export_format[1]:
            file_filter.add_pattern(pattern)
        self.add_filter(file_filter)
