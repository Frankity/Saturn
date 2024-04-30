import gi

gi.require_version('Gtk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gtk, Gdk, Pango, Gio


class RequestWindow(Gtk.Window):
    def __init__(self):
        super().__init__()
        self.set_size_request(200, 340)
        self.set_modal(True)
