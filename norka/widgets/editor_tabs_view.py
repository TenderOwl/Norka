# content_page.py
#
# MIT License
#
# Copyright (c) 2025 Andrey Maksimov <meamka@ya.ru>
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
from pydoc import pager
from typing import Dict, Optional

from gi.repository import Adw, Gtk, GLib, GObject
from loguru import logger

from norka.models import AppState
from norka.define import RESOURCE_PREFIX
from norka.widgets.editor import Editor


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/editor_tabs_view.ui")
class EditorTabsView(Adw.Bin):
    __gtype_name__ = 'EditorTabsView'

    tab_view: Adw.TabView =Gtk.Template.Child()

    pages: Dict[str, Adw.TabPage] = {}
    _appstate: Optional[AppState] = None

    def __init__(self):
        super().__init__()

        self._appstate = Gtk.Application.get_default().props.appstate

        self.tab_view.connect("notify::selected-page", self._on_selected_page_changed)

    def _on_selected_page_changed(self, tab_view: Adw.TabView, param: GObject.GParamSpec):
        page: Adw.TabPage = tab_view.get_selected_page()
        doc_id = None
        for _doc_id, _page in self.pages.items():
            if _page == page:
                doc_id = _doc_id
                break

        logger.debug(doc_id)
        if doc_id:
            self._appstate.current_document_id = doc_id


    def add_tab(self, doc_id: str):
        if doc_id in self.pages:
            page = self.pages[doc_id]
            self.tab_view.set_selected_page(page)
            return

        editor = Editor()
        page: Adw.TabPage = self.tab_view.add_page(editor)
        editor.load_document(int(doc_id))
        page.set_title(editor.document.title)
        self.tab_view.set_selected_page(page)
        self.pages[doc_id] = page

    def close_active_page(self):
        logger.debug('Closing active page')
        if page := self.tab_view.get_selected_page():
            self.tab_view.close_page(page)

    @Gtk.Template.Callback()
    def _on_close_page(self, tab_view: Adw.TabView, page: Adw.TabPage):
        _doc_id = None
        for doc_id, _page in self.pages.items():
            if _page == page:
                _doc_id = doc_id

                editor: Editor = _page.get_child()
                editor.save_document()

                tab_view.close_page_finish(_page, True)
                logger.debug('Removing page for doc {}', doc_id)
                break
        if _doc_id:
            del self.pages[_doc_id]

        return True