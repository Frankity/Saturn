import json

import gi

from ui.widgets.query_item import QueryItem
from ui.widgets.source_view import SourceView
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

        buffer = GtkSource.Buffer()

        sw = Gtk.ScrolledWindow()
        sw.set_margin_top(5)
        sw.set_margin_bottom(5)
        sw.set_margin_start(5)
        sw.set_margin_end(5)

        self.sv = SourceView(buffer, True)

        sw.add(self.sv)

        self.options_query.append_page(self.scrolled_window, Gtk.Label(label="Query"))
        self.options_query.append_page(sw, Gtk.Label(label="Body"))
        self.options_query.append_page(Gtk.Label(label="Params"), Gtk.Label(label="Params"))
        self.options_query.append_page(self.list_box_headers, Gtk.Label(label="Headers"))
        self.options_query.append_page(Gtk.Label(label="Auth"), Gtk.Label(label="Auth"))
        self.options_query.append_page(Gtk.Label(label="Events"), Gtk.Label(label="Events"))

        self.container_box.add(self.options_query)

        def show_menu(widget, event):
            set_selected_row(event)

        self.listbox.connect("row-selected", show_menu)

        self.add_request_to_list()

        def set_selected_row(row):
            self.get_root().set_title('Saturn - (env_test)')
            app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')
            app_settings.set_int('selected-row', row.id)

    def on_setting_changed(self, settings, key):
        try:
            value = settings.get_int(key)
            body_data = (Body
                         .select(Body.body)
                         .where(Body.request == int(value))
                         .first())
            parsed_json = json.loads(body_data.body if body_data is not None else "{}")
            formatted_json = json.dumps(parsed_json, indent=8)
            self.sv.get_buffer().set_text(formatted_json)

        except Exception as e:
            print(e)

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
                self.listbox.append(item_box)
        except Exception as e:
            print(e)
            create_needed_tables()

        self.add(self.container_box)
