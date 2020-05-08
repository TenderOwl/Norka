from gi.repository import Gtk, Granite


class DocumentContextMenu(Gtk.Menu):

    def __init__(self, attach_to=None):
        super().__init__()
        self.attach_to_widget(attach_to)

        export_menu = Gtk.MenuItem(action_name='document.export')
        export_menu.add(Granite.AccelLabel.from_action_name('Export...', 'document.export'))

        rename_menu = Gtk.MenuItem(action_name='document.rename')
        rename_menu.add(Granite.AccelLabel.from_action_name('Rename', 'document.rename'))

        archive_menu = Gtk.MenuItem(action_name='document.archive')
        archive_menu.add(Granite.AccelLabel.from_action_name('Archive', 'document.archive'))

        delete_menu = Gtk.MenuItem(action_name='document.delete')
        delete_menu.add(Granite.AccelLabel.from_action_name('Delete', 'document.delete'))

        self.append(export_menu)
        self.append(Gtk.SeparatorMenuItem())
        self.append(rename_menu)
        self.append(Gtk.SeparatorMenuItem())
        self.append(archive_menu)
        self.append(delete_menu)
        self.show_all()
