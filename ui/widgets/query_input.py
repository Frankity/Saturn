import json
import time

import gi
import urllib3

from core.request_handler import RequestHandler
from utils.database import Requests
from utils.methods import items
from utils.misc import get_name_by_type

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Pango, Gio, GtkSource


class QueryInput(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        request_handler = RequestHandler(main_window_instance)

        self.method_url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.method_url_box.set_margin_start(5)
        self.method_url_box.set_margin_end(5)

        self.entry_url = Gtk.Entry()
        self.entry_url.set_name("entry_url")
        self.entry_url.set_placeholder_text('https://...')
        self.entry_url.set_hexpand(True)
        self.entry_url.set_margin_top(5)
        self.entry_url.set_margin_bottom(0)
        self.entry_url.connect("changed", self.manage_button)
        self.entry_url.connect("activate", request_handler.make_request)

        self.box = Gtk.Box(spacing=10)
        self.icon = Gtk.Image(icon_name="document-send-symbolic")
        self.label = Gtk.Label("Send")
        self.box.add(self.icon)
        self.box.add(self.label)
        self.box.set_tooltip_text('Send request')

        self.send_button = Gtk.Button(child=self.box)
        self.send_button.set_sensitive(False)
        self.send_button.set_margin_top(5)
        self.send_button.set_size_request(80, 30)
        self.send_button.set_halign(Gtk.Align.CENTER)
        self.send_button.set_margin_bottom(0)
        self.send_button.connect("clicked", request_handler.make_request)

        self.save_box = Gtk.Box()
        self.save_icon = Gtk.Image(icon_name='document-save-symbolic')
        self.save_box.add(self.save_icon)
        self.save_box.set_tooltip_text('Save Request')
        self.save_button = Gtk.Button(child=self.save_box)
        self.save_button.set_sensitive(False)
        self.save_button.set_margin_top(5)

        strings = Gtk.ListStore(str)
        for item in [item["name"] for item in items]:
            strings.append([item])

        self.dropdown = Gtk.ComboBox.new_with_model(model=strings)
        renderer_text = Gtk.CellRendererText()
        self.dropdown.pack_start(renderer_text, True)
        self.dropdown.add_attribute(renderer_text, "text", 0)
        self.dropdown.set_active(0)

        self.dropdown.set_margin_top(5)
        self.dropdown.set_margin_bottom(0)

        self.method_url_box.add(self.dropdown)
        self.method_url_box.add(self.entry_url)
        self.method_url_box.add(self.send_button)
        self.method_url_box.add(self.save_button)
        container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        container_box.add(self.method_url_box)
        container_box.set_margin_bottom(5)
        self.add(container_box)

        print(get_name_by_type(self.dropdown.get_active() + 1))

    def manage_button(self, event):
        if self.entry_url.get_text() == "":
            self.send_button.set_sensitive(False)
            self.save_button.set_sensitive(False)
        else:
            self.send_button.set_sensitive(True)
            self.save_button.set_sensitive(True)