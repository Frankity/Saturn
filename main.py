import sys
import gi

from ui.main_window import MyWindow

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

class MyApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        style_provider = Gtk.CssProvider()
        style_provider.load_from_path("custom.css")

        screen = Gdk.Screen.get_default()
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(screen, style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.win = MyWindow(application=app)
        self.win.show_all()  # Gtk.Window.show_all() replaces present()

app = MyApp(application_id="xyz.frankity.saturn")
app.run(sys.argv)
