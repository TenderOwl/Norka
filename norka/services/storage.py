# storage.py
#
# MIT License
#
# Copyright (c) 2020-2022 Andrey Maksimov <meamka@ya.ru>
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
from typing import List, Optional

from gi.repository import GLib

from norka.define import APP_TITLE
from norka.models.document import Document
from norka.models.folder import Folder
from norka.services.logger import Logger


class Storage(object):
    """Class intented to handle data storage operations.

    Current implementation uses SQLite3 database.
    """

    def __init__(self, storage_path: str):
        self.conn = None
        self.version = None
        self.base_path = os.path.join(GLib.get_user_data_dir(), APP_TITLE)
        self.file_path = storage_path

    def connect(self):
        """Connect to the database.
        """
        self.conn = sqlite3.connect(self.file_path,
                                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                                    check_same_thread=False)

    def init(self) -> None:
        """Initialize database and create tables.

        Database path is based on the XDG Base Directory Specification.
        If it not exists then it will be created.

        Also this method checks if database is up to date and apply updates.
        """
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
            Logger.info('Storage folder created at %s', self.base_path)

        Logger.info(f'Storage located at %s', self.file_path)

        self.connect()

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

        if not version or version[0] < 2:
            self.v2_upgrade()

    def v1_upgrade(self) -> bool:
        """Upgrades database to version 1.

        Add fields:
            - created - timestamp document was modified
            - modified - timestamp document was modified
            - tags - list of tags associated with the document
            - order - display order in the documents list

        :return:
        """
        version = 1
        with self.conn:
            try:
                Logger.info(f'Upgrading storage to version: {version}')
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `created` timestamp""")
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `modified` timestamp""")
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `tags` TEXT""")
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `order` INTEGER DEFAULT 0""")
                self.conn.execute("""INSERT INTO `version` VALUES (?, ?)""", (version, datetime.now(),))
                Logger.info(f'Successfully upgraded to v{version}')
                self.version = version
                return True
            except Exception:
                Logger.error(traceback.format_exc())
                return False

    def v2_upgrade(self) -> bool:
        """Upgrades database to version 2.

        Add tables:
            - folders - store folders :)

        Add fields:
            - path - internal path to the document, default to "/"
            - encrypted - indicates whether document is encrypted or not

        :return: True if upgrade was successful, otherwise False
        """
        version = 2
        with self.conn:
            try:
                self.conn.execute("""
                    CREATE TABLE IF NOT EXISTS `folders` (
                        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
                        "path" Text NOT NULL DEFAULT '/',
                        "title" Text NOT NULL,
                        `archived` INTEGER NOT NULL DEFAULT 0,
                        `created` timestamp,
                        `modified` timestamp,
                        CONSTRAINT "uniq_full_path" UNIQUE ( "path", "title" )
                    )
                """)

                Logger.info(f'Upgrading storage to version: {version}')
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `path` TEXT default '/'""")
                self.conn.execute("""ALTER TABLE `documents` ADD COLUMN `encrypted` Boolean default False""")
                self.conn.execute("""INSERT INTO `version` VALUES (?, ?)""", (version, datetime.now(),))
                Logger.info(f'Successfully upgraded to v{version}')
                self.version = version
                return True
            except Exception:
                Logger.error(traceback.format_exc())
                return False

    def count_documents(self, path: str = '/', with_archived: bool = False) -> int:
        """Counts documents in the given path.

        If `with_archived` is True then archived documents will be counted too.
        """
        query = 'SELECT COUNT (1) AS count FROM documents WHERE path=?'
        if not with_archived:
            query += " AND archived=0"
        cursor = self.conn.cursor().execute(query, (path,))
        row = cursor.fetchone()
        Logger.debug(f'{row[0]} documents found in {path}')
        return row[0]

    def count_folders(self, path: str = '/', with_archived: bool = False) -> int:
        """Counts folders in the given path.

        If `with_archived` is True then archived folders will be counted too. Not yet implemented.
        """
        query = 'SELECT COUNT (1) AS count FROM folders WHERE path=?'
        cursor = self.conn.cursor().execute(query, (path,))
        row = cursor.fetchone()
        Logger.debug(f'{row[0]} folders found in {path}')
        return row[0]

    def count_all(self, path: str = '/', with_archived: bool = False) -> int:
        """Counts all documents and folders in the given path.
        
        If `with_archived` is True then archived documents and folders will be counted too.
        """
        folders = self.count_folders(path, with_archived)
        documents = self.count_documents(path, with_archived)
        Logger.debug(f'{folders} folders + {documents} documents found in {path}')
        return folders + documents

    def add_folder(self, title: str, path: str = '/') -> Optional[int]:
        """Creates new folder in the given `path`. Returns ID of created folder.

        By default, folder is created in the root folder.
        """
        if title == '..':
            return None
        cursor = self.conn.cursor().execute(
            "INSERT INTO folders(title, path, created, modified) VALUES (?, ?, ?, ?)",
            (title,
             path,
             datetime.now(),
             datetime.now()
             ), )
        self.conn.commit()
        return cursor.lastrowid

    def rename_folder(self, folder: Folder, title: str) -> bool:
        """Renames folder with given `folder` to `title`.
        """
        if title == '..':
            return False

        query = f"UPDATE folders SET title=? WHERE path=? AND title=?"

        try:
            self.conn.execute(query, (title, folder.path, folder.title,))
            self.conn.commit()

            # Store old path
            old_path = folder.absolute_path
            # Set new title to get the new path
            folder.title = title
            new_path = folder.absolute_path

            self.move_folders(old_path, new_path)
            self.move_documents(old_path, new_path)

        except Exception as e:
            Logger.error(e)
            return False

        return True

    def delete_folders(self, path: str) -> bool:
        """Permanently deletes folders under given `path`
        """
        query = f"DELETE FROM folders WHERE path LIKE ?"

        try:
            self.conn.execute(query, (f'{path}%',))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def delete_folder(self, folder: Folder) -> bool:
        """Permanently deletes `folder`

        :param folder: :class:`Folder` to be deleted.
        """
        query = f"DELETE FROM folders WHERE path=? AND title=?"

        try:
            self.conn.execute(query, (folder.path, folder.title,))
            self.conn.commit()

            self.delete_documents(folder.absolute_path)
            self.delete_folders(folder.absolute_path)
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def add(self, document: Document, path: str = '/') -> int:
        """Creates new document in the given `path`.

        By default, document is created in the root folder.
        """
        cursor = self.conn.cursor().execute(
            "INSERT INTO documents(title, content, path, archived, created, modified) VALUES (?, ?, ?, ?, ?, ?)",
            (document.title,
             document.content,
             document.folder or path,
             document.archived,
             datetime.now(),
             datetime.now()
             ), )
        self.conn.commit()
        return cursor.lastrowid

    def all(self, path: str = '/', with_archived: bool = False, desc: bool = False) -> List[Document]:
        """Returns all documents in the given `path`.

        If `with_archived` is True then archived documents will be returned too.
        `desc` indicates whether to return documents in descending order or not.
        """
        query = "SELECT * FROM documents WHERE path LIKE ?"
        if not with_archived:
            query += " AND archived=0"

        query += f" ORDER BY ID {'desc' if desc else 'asc'}"

        cursor = self.conn.cursor().execute(query, (f'{path}',))
        rows = cursor.fetchall()

        docs = []
        for row in rows:
            docs.append(Document.new_with_row(row))

        return docs

    def get(self, doc_id: int) -> Optional[Document]:
        """Returns document with given `doc_id`.

        """
        query = "SELECT * FROM documents WHERE id=?"
        cursor = self.conn.cursor().execute(query, (doc_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return Document.new_with_row(row)

    def save(self, document: Document) -> bool:
        """Saves `document` to the database.

        """
        query = "UPDATE documents SET title=?, content=?, archived=?, modified=? WHERE id=?"

        try:
            self.conn.execute(query, (document.title, document.content, document.archived, datetime.now()))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def update(self, doc_id: int, data: dict) -> bool:
        """Updates document with given `doc_id` with given `data`.

        `data` can contain any of the following keys:
        - title
        - content
        - archived
        - tags
        - path
        - encrypted

        However, if you need to move document to another folder, you should use :func:`move` method.
        """
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
        """Permanently deletes document with given `doc_id`.

        Returns True if document was deleted successfully.
        """
        query = f"DELETE FROM documents WHERE id=?"

        try:
            self.conn.execute(query, (doc_id,))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def delete_documents(self, path: str) -> bool:
        """Permanently deletes documents under given `path`.

        Returns True if documents were deleted successfully.
        """
        query = 'DELETE FROM documents WHERE path LIKE ?'
        try:
            self.conn.execute(query, (f'{path}%',))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def move_folder(self, folder: Folder, path: str = '/') -> bool:
        """Moves folder to the given `path`.

        Returns True if folder was moved successfully.
        """
        query = 'UPDATE folders SET path=? WHERE path=? AND title=?'

        try:
            self.conn.execute(query, (path, folder.path, folder.title))
            self.conn.commit()

            # Store old path
            old_path = folder.absolute_path
            # Set new title to get the new path
            folder.path = path
            new_path = folder.absolute_path

            self.move_folders(old_path, new_path)
            self.move_documents(old_path, new_path)

        except Exception as e:
            Logger.error(e)
            return False

        return True

    def move(self, doc_id: int, path: str = '/') -> bool:
        """Moves document to the given `path`.

        Returns True if document was moved successfully.
        """
        query = 'UPDATE documents SET path=? WHERE id=?'

        try:
            self.conn.execute(query, (path, doc_id,))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def move_documents(self, old_path: str, new_path: str) -> bool:
        query = f"UPDATE documents SET path=REPLACE(path, ?, ?) WHERE path lIKE ?"

        try:
            self.conn.execute(query, (old_path, new_path, f"{old_path}%",))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def move_folders(self, old_path: str, new_path: str) -> bool:
        query = f"UPDATE folders SET path=REPLACE(path, ?, ?) WHERE path LIKE ?"

        try:
            self.conn.execute(query, (old_path, new_path, f"{old_path}%",))
            self.conn.commit()
        except Exception as e:
            Logger.error(e)
            return False

        return True

    def find(self, search_text: str) -> List[Document]:
        """Finds documents with given `search_text`.
        """
        query = f"SELECT * FROM documents WHERE lower(title) LIKE ? ORDER BY archived ASC"

        cursor = self.conn.cursor().execute(query, (f'%{search_text.lower()}%',))
        rows = cursor.fetchall()

        docs = []
        for row in rows:
            docs.append(Document.new_with_row(row))

        return docs

    def get_folder(self, folder_id: int) -> Optional[Folder]:
        """Returns folder with given `folder_id`.
        """
        query = "SELECT * FROM folders WHERE id=?"
        cursor = self.conn.cursor().execute(query, (folder_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return Folder.new_with_row(row)

    def get_folders(self, path: str = '/', desc: bool = False):
        """Returns all folders under given `path`.

        If `desc` is True then folders will be returned in descending order.
        """
        query = "SELECT * FROM folders WHERE path LIKE ?"

        query += f" ORDER BY title {'desc' if desc else 'asc'}"

        cursor = self.conn.cursor().execute(query, (f'{path}',))
        rows = cursor.fetchall()

        folders = []
        for row in rows:
            folders.append(Folder.new_with_row(row))

        return folders
