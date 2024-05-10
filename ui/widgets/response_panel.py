import json

import gi

from ui.widgets.header_response import HeaderResponse
from ui.widgets.header_status import HeaderStatus
from ui.widgets.source_view import SourceView

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, GtkSource

buffer = GtkSource.Buffer()


class ResponsePanel(Gtk.Notebook):
    def __init__(self):
        super().__init__()

        label1 = Gtk.Label(label="Response")

        sw = Gtk.ScrolledWindow()

        sw.set_margin_top(5)
        sw.set_margin_bottom(5)
        sw.set_margin_start(5)
        sw.set_margin_end(5)

        self.source_view = SourceView(buffer, False)
        self.header_response = HeaderResponse()

        sw.add(self.source_view)

        self.append_page(sw, label1)
        self.append_page(self.header_response, Gtk.Label(label="Headers"))
        self.append_page(Gtk.Label(label="Cookies Tab"), Gtk.Label(label="Cookies"))
