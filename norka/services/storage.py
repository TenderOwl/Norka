# storage.py
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
import sqlite3
import traceback
from datetime import datetime

from gi.repository import GLib

from norka.define import APP_TITLE
from norka.models.document import Document
from norka.services.logger import Logger


class Storage(object):
    def __init__(self):
        self.base_path = os.path.join(GLib.get_user_data_dir(), APP_TITLE)
        self.file_path = os.path.join(self.base_path, 'storage.db')
        self.conn = None
        self.version = None

    def init(self):
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
            Logger.info('Storage folder created at %s', self.base_path)

        Logger.info(f'Storage located at %s', self.file_path)

        self.conn = sqlite3.connect(self.file_path,
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

        self.conn.execute("""
                CREATE TABLE IF NOT EXISTS `documents` (
                    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                    `title` TEXT NOT NULL,
                    `content` TEXT,
                    `archived` INTEGER NOT NULL DEFAULT 0 
                )
            """)

        self.conn.execute("""
                CREATE TABLE IF NOT EXISTS `version` (
                    `version` INTEGER,
                    `timestamp` timestamp
                )
            """)

        # Check if storage DB needs to be upgraded
        version_response = self.conn.execute("""
                SELECT version 
                FROM version 
                ORDER BY timestamp DESC 
                LIMIT 1
            """)
        version = version_response.fetchone()
        Logger.info(f'Current storage version: {version}')
        self.version = version

        if not version or version[0] < 1:
            self.v1_upgrade()

    def v1_upgrade(self):
        """Upgrade databse to version 1.

        Add fields:
            - created - timestamp document was modified
            - modified - timestamp document was modified
            - tags - list of tags associated with the document
            - order - display order in the documents list

        :return:
        """
        with self.conn:
            try:
                Logger.info(f'Upgrading storage to version: {1}')
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `created` timestamp""")
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `modified` timestamp""")
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `tags` TEXT""")
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `order` INTEGER DEFAULT 0""")
                self.conn.execute("""INSERT INTO `version` VALUES (?, ?)""", (1, datetime.now(),))
                Logger.info('Successfully upgraded to v1')
                return True
            except Exception:
                Logger.error(traceback.format_exc())
                return False

    def count(self, with_archived: bool = False) -> int:
        query = 'SELECT COUNT (1) AS count FROM documents'
        if not with_archived:
            query += " WHERE archived=0"
        cursor = self.conn.cursor().execute(query)
        row = cursor.fetchone()
        return row[0]

    def add(self, document: Document) -> int:
        cursor = self.conn.cursor().execute(
            "INSERT INTO documents(title, content, archived, created, modified) VALUES (?, ?, ?, ?, ?)",
            (document.title,
             document.content,
             document.archived,
             datetime.now(),
             datetime.now()
             ), )
        self.conn.commit()
        return cursor.lastrowid

    def all(self, with_archived: bool = False, desc: bool = False) -> list:
        query = "SELECT * FROM documents "
        if not with_archived:
            query += "WHERE archived=0 "

        query += f"ORDER BY ID {'desc' if desc else 'asc'}"

        cursor = self.conn.cursor().execute(query)
        rows = cursor.fetchall()

        docs = []
        for row in rows:
            docs.append(Document.new_with_row(row))

        return docs

    def get(self, doc_id: int) -> Document:
        query = "SELECT * FROM documents WHERE id=?"
        cursor = self.conn.cursor().execute(query, (doc_id,))
        row = cursor.fetchone()

        return Document.new_with_row(row)

    def save(self, document: Document) -> bool:
        query = "UPDATE documents SET title=?, content=?, archived=?, modified=? WHERE id=?"

        try:
            self.conn.execute(query, (document.title, document.content, document.archived, datetime.now()))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def update(self, doc_id: int, data: dict) -> bool:
        fields = {field: value for field, value in data.items()}

        query = f"UPDATE documents SET {','.join(f'{key}=?' for key in fields.keys())}, modified=? WHERE id=?"

        try:
            self.conn.execute(query, tuple(fields.values()) + (datetime.now(), doc_id,))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def delete(self, doc_id: int) -> bool:
        query = f"DELETE FROM documents WHERE id=?"

        try:
            self.conn.execute(query, (doc_id,))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def find(self, search_text: str) -> list:
        query = f"SELECT * FROM documents WHERE lower(title) LIKE ? ORDER BY archived ASC"

        cursor = self.conn.cursor().execute(query, (f'%{search_text.lower()}%',))
        rows = cursor.fetchall()

        docs = []
        for row in rows:
            docs.append(Document.new_with_row(row))

        return docs


storage = Storage()
