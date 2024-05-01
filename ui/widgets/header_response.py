import gi

gi.require_version('Gtk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gtk, Gdk, Pango, Gio, GLib


class HeaderResponse(Gtk.Box):
    def __init__(self, headers=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

    def set_list_store(self, list_store):
        self.treeview = Gtk.TreeView(model=list_store)
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Header", renderer_text, text=0)
        self.treeview.append_column(column_text)

        renderer_description = Gtk.CellRendererText()
        column_description = Gtk.TreeViewColumn("Value", renderer_description, text=1)
        self.treeview.append_column(column_description)
        self.scrolled_window.set_child(self.treeview)
        self.remove(self.scrolled_window)
        self.append(self.scrolled_window)
