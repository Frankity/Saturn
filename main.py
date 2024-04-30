import sys
import gi
from peewee import SqliteDatabase

from models.collection import Collection
from models.requests import Requests
from ui.main_window import MyWindow

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib


class MyApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        db = SqliteDatabase('saturn.db')
        db.connect()
        db.create_tables([Collection, Requests])
    def on_activate(self, app):
        style_provider = Gtk.CssProvider()
        style_provider.load_from_path("custom.css")

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.win = MyWindow(application=app)
        self.win.present()


app = MyApp(application_id="xyz.frankity.saturn")
app.run(sys.argv)
