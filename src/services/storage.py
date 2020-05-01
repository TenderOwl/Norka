import os
import sqlite3

from gi.repository import GLib

from src.define import APP_ID


class Storage(object):
    def __init__(self):
        self.file_path = os.path.join(GLib.get_user_config_dir(), APP_ID, 'storage.db')
        print(f'Storage located at {self.file_path}')


storage = Storage()
