
import gi

from ui.widgets.response_panel import ResponsePanel

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk


class PostRequestContainer(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.response_panel = ResponsePanel()
        self.add(self.response_panel)