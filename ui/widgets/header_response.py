import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gtk, Gdk, Pango, Gio, GLib


class HeaderResponse(Gtk.Box):
    def __init__(self, headers=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.treeview = None
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.add(self.scrolled_window)
        self.scrolled_window.show()

    def set_list_store(self, list_store):
        if self.treeview is None:
            self.treeview = Gtk.TreeView(model=list_store)

            renderer_text = Gtk.CellRendererText()
            column_text = Gtk.TreeViewColumn("Header", renderer_text, text=0)
            self.treeview.append_column(column_text)

            renderer_description = Gtk.CellRendererText()
            column_description = Gtk.TreeViewColumn("Value", renderer_description, text=1)
            self.treeview.append_column(column_description)

            self.scrolled_window.add(self.treeview)
            self.treeview.show()
        else:
            self.treeview.set_model(list_store)
