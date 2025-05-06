from typing import Optional

from gi.repository import GObject


class AppState(GObject.GObject):

    __gtype_name__ = 'AppState'
    __gsignals__ = {
        'path-changed': (GObject.SignalFlags.ACTION, None, (str,)),
        'document-changed': (GObject.SignalFlags.ACTION, None, (str,)),
    }

    _current_path: Optional[str] = None
    _current_document_id: Optional[str] = None

    def __init__(self):
        super().__init__()

    @GObject.Property(type=str)
    def current_path(self) -> str:
        """
        The current path in the notes tree.

        This property represents the current path in the notes tree, which can be
        used to determine the location of folders or documents being viewed or
        interacted with. The path is stored as a string.
        """
        return self._current_path

    @current_path.setter
    def current_path(self, value: str):
        if value == self._current_path:
            return
        self._current_path = value
        self.emit('path-changed', value)

    @GObject.Property(type=str)
    def current_document_id(self) -> str:
        """
        The current document id in the notes tree.

        This property represents the current document id in the notes tree, which can be
        used to determine the location of folders or documents being viewed or
        interacted with. The document id is stored as a string.
        """
        return self._current_document_id

    @current_document_id.setter
    def current_document_id(self, value: str):
        if value == self._current_document_id:
            return
        self._current_document_id = value
        self.emit('document-changed', value)