import sys
import gi

import src.utils.io
from src.ui.main_window import AppWindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class SaturApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.window = None
        self.connect('activate', self.on_activate)
        src.utils.io.create_data_directory()

    def on_activate(self, application):
        self.window = AppWindow(application=application)
        self.window.show_all()


app = SaturApp(application_id="xyz.frankity.saturn")
app.run(sys.argv)
