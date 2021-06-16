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

from gi.repository import Gtk, Granite

from norka.define import RESOURCE_PREFIX
from norka.models.document import Document
from norka.services.stats_handler import DocumentStats


class ExtendedStatsDialog(Granite.Dialog):
    __gtype_name__ = 'ExtendedStatsDialog'

    _document: Document = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_default_size(300, 340)
        self.set_border_width(6)

        self.builder = Gtk.Builder.new_from_resource(f"{RESOURCE_PREFIX}/ui/stats.ui")
        self.main_box = self.builder.get_object("main_box")
        self.title_label: Gtk.Label = self.builder.get_object("title_label")
        self.read_time_label: Gtk.Label = self.builder.get_object("read_time_label")
        self.characters_count_label: Gtk.Label = self.builder.get_object("characters_count_label")
        self.words_count_label: Gtk.Label = self.builder.get_object("words_count_label")
        self.paragraphs_count_label: Gtk.Label = self.builder.get_object("paragraphs_count_label")
        self.created_date_label: Gtk.Label = self.builder.get_object("created_date_label")
        self.modified_date_label: Gtk.Label = self.builder.get_object("modified_date_label")

        self.get_content_area().add(self.main_box)

        close_button = Gtk.Button(label=_("Close"), visible=True)
        close_button.connect('clicked', self.on_close_activated)
        self.add_action_widget(close_button, 0)

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
