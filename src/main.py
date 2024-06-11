import sys
import gi

from src.ui.main_window import AppWindow
from src.utils.database import create_needed_tables
from src.utils.io import create_data_directory

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class SaturApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.window = None
        self.connect('activate', self.on_activate)
        create_data_directory()
        create_needed_tables()

    def on_activate(self, application):
        self.window = AppWindow(application=application)
        self.window.show_all()


app = SaturApp(application_id="xyz.frankity.saturn")
app.run(sys.argv)
