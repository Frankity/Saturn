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
