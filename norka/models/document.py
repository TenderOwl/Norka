# document.py
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
import datetime
import os

from gi.repository import GObject


class Document(GObject.GObject):
    document_id = GObject.property(type=int, default=-1)
    title = GObject.property(type=str)
    content = GObject.property(type=str)
    archived = GObject.property(type=bool, default=False)
    created = GObject.property(type=str)
    modified = GObject.property(type=str)
    folder = GObject.property(type=str)
    encrypted = GObject.property(type=bool, default=False)

    def __init__(self, title: str, content: str = '', folder: str = '/', _id: int = -1,
                 archived=False, encrypted: bool = False,
                 created: str = '-1', modified: str = '-1'):
        GObject.GObject.__init__(self)
        self.document_id = _id
        self.title = title
        self.content = content
        self.folder = folder
        self.archived = archived
        self.encrypted = encrypted
        self.created = created
        self.modified = modified

    @classmethod
    def new_with_row(cls, row: list):
        """Create :class:`Document` instance from sqlite row.

        :param row: row with data from sqlite storage
        :type row: list
        """
        return cls(
            _id=row[0],
            title=row[1],
            content=row[2],
            archived=row[3],
            created=row[4],
            modified=row[5],
            folder=row[8],
            encrypted=row[9],
        )

    @property
    def absolute_path(self):
        return os.path.join(self.folder, self.title)

    def __repr__(self) -> str:
        return f"{self.folder}/{self.title}({self.document_id})"
