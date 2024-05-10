
import gi

from ui.widgets.header_item import HeaderItem
from ui.widgets.response_panel import ResponsePanel
from ui.widgets.source_view import SourceView

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Pango, Gio, GtkSource


class PostRequestContainer(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)
        self.response_panel = ResponsePanel()
        self.add(self.response_panel)