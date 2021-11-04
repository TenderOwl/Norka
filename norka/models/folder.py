# folder.py
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
import datetime
import os.path

from gi.repository import GObject


class Folder(GObject.GObject):
    path = GObject.property(type=str)
    title = GObject.property(type=str)

    # color = GObject.property(type=str)
    # archived = GObject.property(type=bool, default=False)
    # created = GObject.property(type=str)
    # modified = GObject.property(type=str)

    def __init__(self, title: str, path: str = '/'):
        GObject.GObject.__init__(self)
        self.path = path
        self.title = title
        # self.content = content
        # self.archived = archived
        # self.created = created
        # self.modified = modified

    @classmethod
    def new_with_row(cls, row: list):
        """Create :class:`Document` instance from sqlite row

        :param row: row with data from sqlite storage
        :type row: list
        """
        return cls(
            path=row[0],
            title=row[1],
            # content=row[2],
            # archived=row[3],
            # created=row[4],
            # modified=row[5]
        )

    @property
    def normalized_path(self):
        if self.title == '..':
            self.title = ''
        return os.path.join(self.path, self.title)

    def __repr__(self) -> str:
        return f"{self.path} : {self.title}"
