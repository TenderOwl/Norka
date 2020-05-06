# document.py
#
# Copyright 2020 Andrey Maksimov
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE X CONSORTIUM BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# election-box-aluse or other dealings in this Software without prior written
# authorization.


class Document(object):
    __slots__ = ('_id', 'title', 'content', 'archived')

    _id: int
    title: str
    content: str
    archived: bool

    def __init__(self, title: str, content: str = '', _id: int = None, archived=False):
        self._id = _id
        self.title = title
        self.content = content
        self.archived = archived

    @classmethod
    def new_with_row(cls, row: list):
        """Create :class:`Document` instance from sqlite row

        :param row: row with data from sqlite storage
        :type row: list
        """
        return cls(
            _id=row[0],
            title=row[1],
            content=row[2],
            archived=row[3]
        )

    def __repr__(self) -> str:
        return f"{self._id}: {self.title}"
