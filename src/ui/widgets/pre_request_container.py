import gi

from src.ui.widgets.request_headers.request_headers_container import RequestHeadersContainer
from src.ui.widgets.request_params.request_params_container import RequestParamsContainer
from src.ui.widgets.source_view import SourceView

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, GtkSource, Gdk


class PreRequestContainer(Gtk.Box):
    def __init__(self, parent=None):
        self.parent = parent
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.options_query = Gtk.Notebook()
        self.options_query.set_vexpand(True)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

        buffer = GtkSource.Buffer()
        sve_buffer = GtkSource.Buffer()

        sw = Gtk.ScrolledWindow()
        sw.set_margin_top(5)
        sw.set_margin_bottom(5)
        sw.set_margin_start(5)
        sw.set_margin_end(5)

        self.sv = SourceView(buffer, True)
        self.source_view_events = SourceView(sve_buffer, editable=True, for_events=True, pr=parent)
        self.sve_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        self.rev_label = Gtk.Label(label="")

        self.rev_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.rev_box.set_size_request(-1, 50)
        self.rev_box.modify_bg(Gtk.StateFlags.NORMAL, Gdk.Color(red=65535, green=0, blue=0))
        self.rev_box.add(self.rev_label)

        self.revealer = Gtk.Revealer()
        self.revealer.set_reveal_child(False)
        self.revealer.add(self.rev_box)

        self.sve_box.add(self.source_view_events)
        self.sve_box.add(self.revealer)

        sw.add(self.sv)

        self.language_manager = GtkSource.LanguageManager.new()
        self.json_lang = self.language_manager.get_language("python")
        self.source_view_events.get_buffer().set_language(self.json_lang)

        self.request_headers_container = RequestHeadersContainer()
        self.request_params_container = RequestParamsContainer(parent)

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
        self.options_query.append_page(self.sve_box, Gtk.Label(label="Events"))

        self.add(self.options_query)
