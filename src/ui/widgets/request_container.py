import json
from urllib.parse import urlparse, parse_qs, urlencode

import gi

from src.ui.widgets.header_status import HeaderStatus
from src.ui.widgets.post_response_container import PostRequestContainer
from src.ui.widgets.pre_request_container import PreRequestContainer
from src.ui.widgets.query_input import QueryInput
from src.ui.widgets.request_headers.header_item import HeaderItem
from src.ui.widgets.request_params.param_item import ParamItem
from src.ui.widgets.windows.environment_window import EnvironmentWindow
from src.utils.database import Body, Requests, Headers, Params, Response, Environments, Events

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk


def manual_encode(params):
    encoded_params = []
    for key, value in params.items():
        encoded_key = key.replace(' ', '+')  # Replace spaces with '+'
        encoded_value = value.replace(' ', '+')  # Replace spaces with '+'
        encoded_params.append(f"{encoded_key}={encoded_value}")

    query_string = '&'.join(encoded_params)
    return query_string


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

        envs = Gtk.ListStore(int, str)
        for env in Environments.select():
            envs.append([env.id, env.name])

        self.env_label = Gtk.Label(label='Environment:')
        self.env_label.set_xalign(2)
        self.env_label.set_hexpand(True)
        self.combo_box_environment = Gtk.ComboBox.new_with_model(model=envs)
        renderer_text = Gtk.CellRendererText()
        self.combo_box_environment.pack_start(renderer_text, True)
        self.combo_box_environment.add_attribute(renderer_text, "text", 1)
        self.combo_box_environment.set_active(0)

        self.box = Gtk.Box(spacing=0)
        self.icon = Gtk.Image(icon_name="emblem-system-symbolic")
        self.box.add(self.icon)
        self.box.set_tooltip_text('Manage Environments')
        self.menu_button = Gtk.Button(child=self.box)
        self.menu_button.connect('clicked', self.show_environments_dialog)

        self.combo_box_environment.set_hexpand(False)

        self.box_header_container.add(self.header_status)
        self.box_header_container.add(self.env_label)
        self.box_header_container.add(self.combo_box_environment)
        self.box_header_container.add(self.menu_button)

        self.add(self.box_header_container)

        self.notebook_response = Gtk.Notebook()

        self.pre_request_container = PreRequestContainer(self)
        self.post_request_container = PostRequestContainer()

        paned = Gtk.Paned()

        paned.pack1(self.pre_request_container)
        paned.pack2(self.post_request_container)

        self.query_input = QueryInput(main_window_instance)

        self.add(self.query_input)
        self.add(paned)

    def on_setting_changed(self, settings, key):
        try:
            value = settings.get_int(key)
            body_data = (Body
                         .select(Body.body)
                         .where(Body.request == int(value))
                         .first())

            request_data = (Requests
                            .select()
                            .where(Requests.id == int(value))
                            .first())

            response_data = (Response
                             .select()
                             .where(Response.request == int(value))
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

            events_data = Events.select().where(Events.request == int(value)).first()

            parsed_json = json.loads(body_data.body if body_data is not None else "{}")
            formatted_json = json.dumps(parsed_json, indent=8)

            self.pre_request_container.sv.get_buffer().set_text(formatted_json)
            if request_data.url is not None:
                self.query_input.entry_url.set_text(request_data.url)
            else:
                self.query_input.entry_url.set_text("")
            self.query_input.dropdown.set_active(request_data.method - 1)
            self.get_headers(headers_data)
            self.get_query_params(params_data, request_data)

            if response_data is not None:
                self.post_request_container.response_panel.source_view.get_buffer() \
                    .set_text(response_data.body, len(response_data.body))
            else:
                self.post_request_container.response_panel.source_view.get_buffer().set_text("", 0)

            if events_data is not None:
                self.pre_request_container.source_view_events.get_buffer().set_text(
                    events_data.event, len(events_data.event)
                )
            else:
                self.pre_request_container.source_view_events.get_buffer().set_text("", 0)


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
            param_item = ParamItem(parent=self, key=param.key, value=param.value, hid=param.id, request=param.request,
                                   enabled=param.enabled)
            self.pre_request_container.request_params_container.list_box_params.add(param_item)

        param_object = {}
        for param in params_data:
            if param.enabled:
                param_object[param.key] = param.value

        query_string = manual_encode(param_object)

        if query_string:
            self.query_input.entry_url.set_text(f"{request_data.url}?{query_string}")

    def get_kv(self):
        param_list = {}
        for existing_param in self.pre_request_container.request_params_container.list_box_params.get_children():
            if isinstance(existing_param, ParamItem) and existing_param.enabled:
                param_list[existing_param.key] = existing_param.value

        query_string = manual_encode(param_list)

        if query_string:
            self.query_input.entry_url.set_text(f"{self.get_url_only()}?{query_string}")

    def update_params(self, enabled: bool, param: str):
        url = self.query_input.entry_url.get_text()
        parsed_url = urlparse(url)

        param_list = {}
        for existing_param in self.pre_request_container.request_params_container.list_box_params.get_children():
            if isinstance(existing_param, ParamItem) and existing_param.enabled:
                param_list[existing_param.key] = existing_param.value

        query_params = parse_qs(parsed_url.query)

        if enabled:

            query_params.pop(param, None)
        else:
            if param is not None:
                param_object = self.get_param_value(param)
                query_params[param] = param_object.get(param)

        modified_query_string = urlencode(query_params, doseq=True)
        modified_url = parsed_url._replace(query=modified_query_string).geturl()
        self.query_input.entry_url.set_text(modified_url)

    def get_param_value(self, param: str):
        param_object = {}
        for existing_param in self.pre_request_container.request_params_container.list_box_params.get_children():
            if isinstance(existing_param, ParamItem) and existing_param.key == param:
                param_object[existing_param.key] = existing_param.value
                break
        return param_object

    def get_url_only(self):
        parsed_url = urlparse(self.query_input.entry_url.get_text())
        return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

    def show_environments_dialog(self, widget):
        environments_dialog = EnvironmentWindow(main_window_instance=self, modify=False)
        environments_dialog.show()
