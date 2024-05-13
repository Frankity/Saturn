import gi

from ui.widgets.request_headers.request_headers_container import RequestHeadersContainer
from ui.widgets.request_params.request_params_container import RequestParamsContainer
from ui.widgets.source_view import SourceView

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, GtkSource


class PreRequestContainer(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.options_query = Gtk.Notebook()
        self.options_query.set_vexpand(True)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

        buffer = GtkSource.Buffer()

        sw = Gtk.ScrolledWindow()
        sw.set_margin_top(5)
        sw.set_margin_bottom(5)
        sw.set_margin_start(5)
        sw.set_margin_end(5)

        self.sv = SourceView(buffer, True)

        sw.add(self.sv)

        self.request_headers_container = RequestHeadersContainer()
        self.request_params_container = RequestParamsContainer()

        self.scrolled_window_headers = Gtk.ScrolledWindow()
        self.scrolled_window_params = Gtk.ScrolledWindow()
        self.scrolled_window_headers.set_hexpand(True)
        self.scrolled_window_headers.set_vexpand(True)
        self.scrolled_window_params.set_hexpand(True)
        self.scrolled_window_params.set_hexpand(True)
        self.scrolled_window_headers.add(self.request_headers_container)
        self.scrolled_window_params.add(self.request_params_container)

        self.options_query.append_page(self.scrolled_window_params, Gtk.Label(label="Params"))
        self.options_query.append_page(sw, Gtk.Label(label="Body"))
        self.options_query.append_page(self.scrolled_window_headers, Gtk.Label(label="Headers"))
        self.options_query.append_page(Gtk.Label(label="Auth"), Gtk.Label(label="Auth"))
        self.options_query.append_page(Gtk.Label(label="Events"), Gtk.Label(label="Events"))

        self.add(self.options_query)
