import json

import gi

from ui.widgets.header_item import HeaderItem
from ui.widgets.source_view import SourceView
from utils.database import Body

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Pango, Gio, GtkSource


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

        self.header_headers_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.label_header_description = Gtk.Label()
        self.label_header_description.set_xalign(0)
        self.label_header_description.set_hexpand(True)
        self.label_header_description.set_margin_top(0)
        self.label_header_description.set_margin_start(10)
        self.label_header_description.set_markup("<span weight='light' size='large'>HTTP Headers</span>")
        self.header_headers_container.add(self.label_header_description)

        self.list_box_headers = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.list_box_headers.set_margin_top(0)
        self.list_box_headers.set_hexpand(True)

        self.box = Gtk.Box()
        self.icon = Gtk.Image(icon_name="list-add-symbolic")
        self.box.add(self.icon)
        self.box.set_tooltip_text('Add Header')
        self.button = Gtk.Button(child=self.box)
        self.button.set_name("add-button")
        self.button.set_margin_top(10)
        self.button.set_margin_end(10)
        self.button.connect("clicked", lambda button: self.list_box_headers.add(HeaderItem()))
        self.header_headers_container.add(self.button)

        self.list_box_headers.add(self.header_headers_container)

        self.scrolled_window_headers = Gtk.ScrolledWindow()
        self.scrolled_window_headers.set_hexpand(True)
        self.scrolled_window_headers.set_vexpand(True)
        self.scrolled_window_headers.add(self.list_box_headers)

        self.options_query.append_page(Gtk.Label(label="Params"), Gtk.Label(label="Params"))
        self.options_query.append_page(sw, Gtk.Label(label="Body"))
        self.options_query.append_page(self.scrolled_window_headers, Gtk.Label(label="Headers"))
        self.options_query.append_page(Gtk.Label(label="Auth"), Gtk.Label(label="Auth"))
        self.options_query.append_page(Gtk.Label(label="Events"), Gtk.Label(label="Events"))

        self.add(self.options_query)
