import json
import gi

from ui.widgets.header_item import HeaderItem
from ui.widgets.header_status import HeaderStatus
from ui.widgets.post_response_container import PostRequestContainer
from ui.widgets.pre_request_container import PreRequestContainer
from ui.widgets.query_input import QueryInput
from utils.database import Body, Requests, Headers
from utils.misc import get_name_by_type

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Pango, Gio, GtkSource


class RequestContainer(Gtk.Box):
    def __init__(self, main_window_instance=None):
        self.main_window_instance = main_window_instance
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.box_header_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.box_header_container.set_hexpand(True)
        self.box_header_container.set_margin_top(15)
        self.box_header_container.set_margin_start(10)
        self.box_header_container.set_margin_end(10)
        self.box_header_container.set_margin_bottom(15)

        self.header_status = HeaderStatus(self)

        strings = Gtk.ListStore(str)
        item = "Default"
        strings.append([item])
        self.env_label = Gtk.Label(label='Environment:')
        self.env_label.set_xalign(2)
        self.env_label.set_hexpand(True)
        self.combo_box_environment = Gtk.ComboBox.new_with_model(model=strings)
        renderer_text = Gtk.CellRendererText()
        self.combo_box_environment.pack_start(renderer_text, True)
        self.combo_box_environment.add_attribute(renderer_text, "text", 0)
        self.combo_box_environment.set_active(0)

        self.combo_box_environment.set_hexpand(False)

        self.box_header_container.add(self.header_status)
        self.box_header_container.add(self.env_label)
        self.box_header_container.add(self.combo_box_environment)

        self.add(self.box_header_container)

        self.notebook_response = Gtk.Notebook()

        self.pre_request_container = PreRequestContainer()
        self.post_request_container = PostRequestContainer()

        paned = Gtk.Paned()

        paned.pack1(self.pre_request_container)
        paned.pack2(self.post_request_container)

        self.notebook_content = QueryInput(self)

        self.notebook_response.append_page(self.notebook_content, Gtk.Label(label="Params"))

        self.add(self.notebook_response)
        self.add(paned)

    def on_setting_changed(self, settings, key):
        try:
            value = settings.get_int(key)
            body_data = (Body
                         .select(Body.body)
                         .where(Body.request == int(value))
                         .first())
            request_data = (Requests
                            .select(Requests.name,
                                    Requests.url,
                                    Requests.type)
                            .where(Requests.id == int(value))
                            .first())

            headers_data = (Headers
                            .select(Headers.key,
                                    Headers.value,
                                    Headers.id)
                            .where(Headers.request == int(value)))

            parsed_json = json.loads(body_data.body if body_data is not None else "{}")
            formatted_json = json.dumps(parsed_json, indent=8)

            self.pre_request_container.sv.get_buffer().set_text(formatted_json)
            self.notebook_content.entry_url.set_text(request_data.url)
            self.notebook_content.dropdown.set_active(request_data.type - 1)
            self.notebook_response.set_tab_label(self.notebook_content, Gtk.Label(label=request_data.name))

            for header in headers_data:

                header_item = HeaderItem(key=header.key, value=header.value, hid=header.id,  request=header.request)
                self.pre_request_container.list_box_headers.add(header_item)

        except Exception as e:
            print(e)
