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

from gi.repository import Adw, Gtk

from norka.define import RESOURCE_PREFIX
from norka.widgets.welcome_page import WelcomePage
from norka.widgets.editor_tabs_view import EditorTabsView
from norka.services import Storage


@Gtk.Template(resource_path=f"{RESOURCE_PREFIX}/ui/content_page.ui")
class ContentPage(Adw.NavigationPage):
    __gtype_name__ = 'ContentPage'

    screens: Adw.ViewStack = Gtk.Template.Child()
    welcome_page: WelcomePage = Gtk.Template.Child()
    editor_tabs_view: EditorTabsView = Gtk.Template.Child()

    storage: Storage

    def __init__(self):
        super().__init__()

        self.storage = Gtk.Application.get_default().props.storage

        # Set default page to welcome page if there are no documents
        if self.storage.count_all() == 0:
            self.screens.set_visible_child_name('welcome-page')
        else:
            self.screens.set_visible_child_name('content-page')

    def document_open(self, doc_id: str):
        self.editor_tabs_view.add_tab(doc_id)