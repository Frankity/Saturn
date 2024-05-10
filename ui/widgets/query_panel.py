import json

import gi

from ui.widgets.query_item import QueryItem
from utils.database import Body, Requests, create_needed_tables

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Pango, Gio, GtkSource

from ui.widgets.header_item import HeaderItem


class QueryPanel(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.listbox = Gtk.ListBox()
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

        self.options_query = Gtk.Notebook()
        self.options_query.set_vexpand(True)

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

        self.scrolled_window.add(self.listbox)

        def set_selected_row(row):
            app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')
            app_settings.set_int('selected-row', row.id)

        self.add(self.scrolled_window)

        def show_menu(widget, event):
            set_selected_row(event)

        self.listbox.connect("row-selected", show_menu)

        self.add_request_to_list()

    def clear_list(self):
        request_items = Requests.select().count()
        for i in range(request_items):
            row = self.listbox.get_row_at_index(i)
            if row is not None:
                self.listbox.remove(row)
        self.add_request_to_list()

    def add_request_to_list(self):
        self.listbox.bind_model()
        requests = Requests.select()
        try:
            for request in requests:
                item_box = QueryItem(request)
                self.listbox.add(item_box)
        except Exception as e:
            print(e)
            create_needed_tables()

        self.add(self.container_box)
