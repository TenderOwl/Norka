# extended_stats_dialog.py
#
# MIT License
#
# Copyright (c) 2021 Andrey Maksimov <meamka@ya.ru>
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
from datetime import datetime
from gettext import gettext as _

from gi.repository import Gtk, Adw

from norka.define import RESOURCE_PREFIX
from norka.models.document import Document
from norka.services.stats_handler import DocumentStats


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/stats.ui")
class ExtendedStatsWindow(Adw.Window):
    __gtype_name__ = 'ExtendedStatsWindow'

    _document: Document = None

    main_box = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()
    read_time_label: Gtk.Label = Gtk.Template.Child()
    characters_count_label: Gtk.Label = Gtk.Template.Child()
    words_count_label: Gtk.Label = Gtk.Template.Child()
    paragraphs_count_label: Gtk.Label = Gtk.Template.Child()
    created_date_label: Gtk.Label = Gtk.Template.Child()
    modified_date_label: Gtk.Label = Gtk.Template.Child()
    export_text: Gtk.Button = Gtk.Template.Child()
    export_markdown: Gtk.Button = Gtk.Template.Child()
    export_html: Gtk.Button = Gtk.Template.Child()

    def __init__(self, window, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(300, 340)
        self.set_transient_for(window)

        self.export_text.connect('clicked', window.on_export_plaintext)
        self.export_markdown.connect('clicked', window.on_export_markdown)
        self.export_html.connect('clicked', window.on_export_html)


    @property
    def document(self):
        return self._document

    @document.setter
    def document(self, document: Document):
        self._document = document
        self.title_label.set_label(self._document.title)
        self.title_label.set_tooltip_text(self._document.title)
        created = datetime.strptime(document.created, "%Y-%m-%d %H:%M:%S.%f")
        self.created_date_label.set_label(datetime.strftime(created, "%a, %d %b %Y"))
        self.created_date_label.set_tooltip_text(datetime.strftime(created, "%a, %d %b %Y %H:%M:%S"))
        modified = datetime.strptime(document.modified, "%Y-%m-%d %H:%M:%S.%f")
        self.modified_date_label.set_label(datetime.strftime(modified, "%a, %d %b %Y"))
        self.modified_date_label.set_tooltip_text(datetime.strftime(modified, "%a, %d %b %Y %H:%M:%S"))

    def update_stats(self, stats: DocumentStats):
        self.characters_count_label.set_label(f"{stats.characters}")
        self.words_count_label.set_label(f"{stats.words}")
        self.paragraphs_count_label.set_label(f"{stats.paragraphs}")
        self.read_time_label.set_label(_("{:d}h {:02d}m {:02d}s").format(*stats.read_time))

    def on_close_activated(self, sender: Gtk.Widget):
        self.hide()
