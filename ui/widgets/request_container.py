import json
import gi
import urllib3

from ui.widgets.request_headers.header_item import HeaderItem
from ui.widgets.header_status import HeaderStatus
from ui.widgets.post_response_container import PostRequestContainer
from ui.widgets.pre_request_container import PreRequestContainer
from ui.widgets.query_input import QueryInput
from ui.widgets.request_params.param_item import ParamItem
from utils.database import Body, Requests, Headers, Params

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk


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

            params_data = (Params
                           .select(
                Params.key,
                Params.value,
                Params.id,
                Params.enabled)
                           .where(Params.request == int(value)))

            parsed_json = json.loads(body_data.body if body_data is not None else "{}")
            formatted_json = json.dumps(parsed_json, indent=8)

            self.pre_request_container.sv.get_buffer().set_text(formatted_json)
            self.notebook_content.entry_url.set_text(request_data.url)
            self.notebook_content.dropdown.set_active(request_data.type - 1)
            self.notebook_response.set_tab_label(self.notebook_content, Gtk.Label(label=request_data.name))

            self.get_headers(headers_data)

            self.get_query_params(params_data, request_data)

        except Exception as e:
            print(e)

    def get_headers(self, headers_data):
        for existing_header in self.pre_request_container.request_headers_container.list_box_headers.get_children():
            if isinstance(existing_header, HeaderItem):
                self.pre_request_container.request_headers_container.list_box_headers.remove(existing_header)

        for header in headers_data:
            header_item = HeaderItem(key=header.key, value=header.value, hid=header.id, request=header.request)
            self.pre_request_container.request_headers_container.list_box_headers.add(header_item)

    def get_query_params(self, params_data, request_data):

        for existing_param in self.pre_request_container.request_params_container.list_box_params.get_children():
            if isinstance(existing_param, ParamItem):
                self.pre_request_container.request_params_container.list_box_params.remove(existing_param)

        for param in params_data:
            param_item = ParamItem(key=param.key, value=param.value, hid=param.id, request=param.request, enabled=param.enabled)
            self.pre_request_container.request_params_container.list_box_params.add(param_item)

        param_object = {}
        for param in params_data:
            if param.enabled:
                param_object[param.key] = param.value

        query_string = self.manual_encode(param_object)

        if query_string:
            self.notebook_content.entry_url.set_text(f"{request_data.url}?{query_string}")

    def manual_encode(self, params):
        encoded_params = []
        for key, value in params.items():
            encoded_key = key.replace(' ', '+')  # Replace spaces with '+'
            encoded_value = value.replace(' ', '+')  # Replace spaces with '+'
            encoded_params.append(f"{encoded_key}={encoded_value}")

        query_string = '&'.join(encoded_params)
        return query_string

        #def set_query_params_to_url(self, params):


        #query_string = urllib3.request.urlencode(params)


