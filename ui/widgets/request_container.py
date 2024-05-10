import json
import time

import gi
import urllib3

from models.response_data import ResponseData
from ui.widgets.header_status import HeaderStatus
from ui.widgets.post_response_container import PostRequestContainer
from ui.widgets.pre_request_container import PreRequestContainer
from ui.widgets.query_input import QueryInput
from utils.database import Body, Requests
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

        self.combo_box_environment = Gtk.Label(label='Sample-Saturn-Collection')
        self.combo_box_environment.set_xalign(2)
        self.combo_box_environment.set_hexpand(True)

        self.box_header_container.add(self.header_status)
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

            parsed_json = json.loads(body_data.body if body_data is not None else "{}")
            formatted_json = json.dumps(parsed_json, indent=8)

            self.pre_request_container.sv.get_buffer().set_text(formatted_json)
            self.notebook_content.entry_url.set_text(request_data.url)
            self.notebook_content.dropdown.set_active(request_data.type - 1)
            self.notebook_response.set_tab_label(self.notebook_content, Gtk.Label(label=request_data.name))

        except Exception as e:
            print(e)

    def make_request(self, event):
        from ui.main_window import app_settings

        request = (Requests
                   .select(Requests.type, Requests.url)
                   .where(Requests.id == app_settings.get_int('selected-row'))
                   .first())
        http = urllib3.PoolManager()
        liststore = Gtk.ListStore(str, str)
        method = get_name_by_type(self.notebook_content.dropdown.get_active() + 1) # indexed

        start_iter = self.pre_request_container.sv.get_buffer().get_start_iter()
        end_iter = self.pre_request_container.sv.get_buffer().get_end_iter()
        body = self.pre_request_container.sv.get_buffer().get_text(start_iter, end_iter, True)

        response_failure_data = {
            'status': 0,
            'elapsed': 0,
            'headers': {'Content-Length': 0}
        }
        response_fail = ResponseData(
            response_failure_data['status'],
            response_failure_data['elapsed'],
            response_failure_data['headers']
        )

        try:
            start_time = time.time()
            resp = http.request(
                method=get_name_by_type(request.type),
                url=self.notebook_content.entry_url.get_text(),
                body=body if method in ["POST", "PUT", "PATCH"] else None,
                headers={'Content-Type': 'application/json'},
            )

            end_time = time.time()

            elapsed = end_time - start_time
            resp.elapsed = elapsed

            parsed = json.loads(resp.data)

            for header in resp.headers:
                liststore.append([header, resp.headers[header]])

            self.header_status.update_data(resp)

            formatted_json = json.dumps(parsed, indent=8, sort_keys=True)

            self.post_request_container.response_panel.header_response.set_list_store(liststore)
            self.post_request_container.response_panel.source_view.get_buffer().set_text(formatted_json)

        except urllib3.exceptions.HTTPWarning as e:
            # Handle urllib3 exceptions here
            print("URLError:", e)
            self.post_request_container.response_panel.source_view.get_buffer().set_text(str(e.args), len(str(e.args)))
            # Set header even in case of error
            self.header_status.update_data(response_fail)

        except urllib3.exceptions.HTTPError as e:
            print("HTTPError:", e)
            self.post_request_container.response_panel.source_view.get_buffer().set_text(str(e.args), len(str(e.args)))
            # Set header even in case of error
            self.header_status.update_data(response_fail)

        except Exception as e:
            # Handle other exceptions here
            print("An unexpected error occurred:", e)
            self.post_request_container.response_panel.source_view.get_buffer().set_text(str(e.args), len(str(e.args)))
            # Set header even in case of error
            self.header_status.update_data(response_fail)

        finally:
            # Any cleanup or final actions can go here
            pass
