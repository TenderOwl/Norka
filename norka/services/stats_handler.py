# stats_handler.py
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


from collections import namedtuple
from gettext import gettext as _

from gi.repository import GtkSource, GObject

from norka.services.stats_counter import StatsCounter

DocumentStats = namedtuple('Stats', ['characters', 'words', 'sentences', 'paragraphs', 'read_time'])


class StatsHandler(GObject.GObject):
    """Shows a default statistic on the stats button, and allows the user to toggle which one."""

    # Must match the order/index defined in gschema.xml
    CHARACTERS = 0
    WORDS = 1
    SENTENCES = 2
    PARAGRAPHS = 3
    READ_TIME = 4

    __gsignals__ = {
        'update-document-stats': (GObject.SignalFlags.ACTION, None, ()),
    }

    def __init__(self, buffer: GtkSource.Buffer):
        super().__init__()

        self.buffer = buffer
        self.buffer.connect("changed", self.on_text_changed)

        self.stats = DocumentStats(0, 0, 0, 0, (0, 0, 0))

        self.stats_counter = StatsCounter(self.update_stats)

    def on_text_changed(self, buf):
        self.stats_counter.count(buf.get_text(buf.get_start_iter(), buf.get_end_iter(), False))

    # def get_text_for_stat(self, stat):
    #     if stat == self.CHARACTERS:
    #         return _("{:n} Characters").format(self.characters)
    #     elif stat == self.WORDS:
    #         return _("{:n} Words").format(self.words)
    #     elif stat == self.SENTENCES:
    #         return _("{:n} Sentences").format(self.sentences)
    #     elif stat == self.PARAGRAPHS:
    #         return _("{:n} Paragraphs").format(self.paragraphs)
    #     elif stat == self.READ_TIME:
    #         return _("{:d}:{:02d}:{:02d} Read Time").format(*self.read_time)
    #     else:
    #         raise ValueError("Unknown stat {}".format(stat))

    def update_stats(self, stats):
        self.stats = DocumentStats(*stats)
        self.emit('update-document-stats')

    def on_destroy(self, _widget):
        self.stats_counter.stop()
