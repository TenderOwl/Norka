import os.path
from unittest import TestCase

from norka.define import STORAGE_NAME, DB_VERSION
from norka.models.document import Document
from norka.models.folder import Folder
from norka.services.storage import Storage


class StorageTests(TestCase):

    def setUp(self) -> None:
        self.storage_name = 'test-' + STORAGE_NAME
        print(f'Initializind {self.storage_name}')

        storage_path = os.path.join('test-' + STORAGE_NAME)
        self.storage = Storage(storage_path)
        self.storage.init()

    def tearDown(self) -> None:
        print(f'Unlinking {self.storage.file_path}')
        os.remove(self.storage.file_path)

    def _create_document(self, path: str = "/"):
        document = Document('Test Document', "# Simple test content", path)
        return self.storage.add(document)

    def test_init(self):
        self.assertEqual(self.storage.file_path, self.storage_name)

    def test_upgrade(self):
        self.assertEqual(self.storage.version, DB_VERSION)

    def test_create_document(self):
        doc_id = self._create_document()
        self.assertIsNotNone(doc_id)
        doc = self.storage.get(doc_id)
        self.assertEqual(doc.title, 'Test Document')
        self.assertEqual(doc.content, "# Simple test content")
        self.assertEqual(doc.folder, "/")

    def test_create_document_at_path(self):
        doc_id = self._create_document('/non-root')
        doc = self.storage.get(doc_id)
        self.assertEqual(doc.title, 'Test Document')
        self.assertEqual(doc.content, "# Simple test content")
        self.assertEqual(doc.folder, "/non-root")

    def test_delete_document(self):
        doc_id = self._create_document()
        self.storage.delete(doc_id)
        self.assertIsNone(self.storage.get(doc_id))

    def test_update_document(self):
        doc_id = self._create_document()
        self.assertEqual(self.storage.get(doc_id).title, 'Test Document')

        self.storage.update(doc_id, {'title': 'Updated title'})
        self.assertEqual(self.storage.get(doc_id).title, 'Updated title')

    def test_move_document(self):
        doc_id = self._create_document()
        moved = self.storage.move(doc_id, '/non/root/path')

        self.assertTrue(moved)

        doc = self.storage.get(doc_id)
        self.assertEqual(doc.folder, '/non/root/path')

    def test_archive_document(self):
        doc_id = self._create_document()
        self.storage.update(doc_id, {'archived': True})

        doc = self.storage.get(doc_id)
        self.assertTrue(doc.archived)

    def test_unarchive_document(self):
        doc_id = self._create_document()
        self.storage.update(doc_id, {'archived': True})
        self.storage.update(doc_id, {'archived': False})

        doc = self.storage.get(doc_id)
        self.assertFalse(doc.archived)

    def test_count_documents(self):
        self._create_document()
        self._create_document('/non/root')

        count = self.storage.count_documents()
        self.assertEqual(count, 1)

    def test_count_documents_with_archived(self):
        self._create_document()
        doc2_id = self._create_document()

        self.storage.update(doc2_id, {'archived': True})

        count = self.storage.count_documents(with_archived=True)
        self.assertEqual(count, 2)

    def test_create_folder(self):
        folder_id = self.storage.add_folder('Test Folder')
        folder = self.storage.get_folder(folder_id)
        self.assertEqual(folder.title, 'Test Folder')
        self.assertEqual(folder.path, '/')
