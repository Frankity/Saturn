import sys
import gi

from src.ui.main_window import AppWindow
from src.utils.database import create_needed_tables
from src.utils.io import create_data_directory

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio


class SaturApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.window = None
        self.connect('activate', self.on_activate)
        self.connect("shutdown", self.close_event)
        create_data_directory()
        create_needed_tables()

    def close_event(self, application):
        app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')
        app_settings.set_int('selected-row', 0)

    def on_activate(self, application):
        self.window = AppWindow(application=application)
        self.window.show_all()


app = SaturApp(application_id="xyz.frankity.saturn")
app.run(sys.argv)
