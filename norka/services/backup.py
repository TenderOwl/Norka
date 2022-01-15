# backup.py
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
import os
from os import path
from typing import Optional

from gi.repository import GObject

from norka.define import STORAGE_NAME
from norka.models.document import Document
from norka.services.settings import Settings
from norka.services.storage import Storage


class BackupService(GObject.GObject):
    __gtype_name__ = 'BackupService'
    __gsignals__ = {
        'started': (GObject.SignalFlags.ACTION, None, (str, int,)),
        'finished': (GObject.SignalFlags.ACTION, None, ()),
    }

    storage: Storage

    def __init__(self, settings: Settings):
        GObject.GObject.__init__(self)

        self.settings = settings

        # Init storage location and SQL structure
        storage_path = self.settings.get_string("storage-path")
        if not storage_path:
            storage_path = os.path.join(self.base_path, STORAGE_NAME)
            self.settings.set_string("storage-path", storage_path)

        self.storage = Storage(storage_path)
        self.storage.connect()

    def save(self, backup_dir: str) -> Optional[str]:
        if not path.exists(backup_dir):
            return None

        # We have to implement the same folder structure as we have inside our storage.
        # Thus, we need to:
        # - export all documents from the root `/`
        # - find all folders and recreate them on the real filesystem
        # - export all the documents inside
        self.emit('started', backup_dir, -1)

        docs = self.storage.all(path='/', with_archived=True)

        for doc in docs:
            self._write_document(doc, backup_dir)

        folders = self.storage.get_folders(path='%')
        for folder in folders:
            folder_path = os.path.join(backup_dir, folder.absolute_path[1:])
            os.makedirs(folder_path, exist_ok=True)

            docs = self.storage.all(path=folder.absolute_path, with_archived=True)

            for doc in docs:
                self._write_document(doc, folder_path)

        self.emit('finished')
        return backup_dir

    def _write_document(self, doc: Document, backup_dir: str) -> bool:
        filename = path.join(backup_dir, doc.title)
        if doc.archived:
            filename += '-archived'

        try:
            with open(filename + '.md', 'w') as fd:
                fd.writelines(doc.content)
            return True
        except Exception as e:
            print(e)
            return False
