from gi.repository import GObject

from norka.models.document import Document


class DocumentManager(GObject.GObject):
    __gtype_name__ = 'DocumentManager'

    __gsignals__ = {
        'current-document-changed': (GObject.SignalFlags.ACTION, None, (int,)),
    }

    _current_document: Document | None

    def __init__(self):
        super().__init__()

    @GObject.Property(type=GObject.TYPE_PYOBJECT)
    def current_document(self):
        return self._current_document

    @current_document.setter
    def current_document(self, document: Document):
        self._current_document = document
        self.emit('current-document-changed', self._current_document.document_id)


document_manager = DocumentManager()
