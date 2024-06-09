import json
import time
import urllib3
from urllib3.exceptions import (
    MaxRetryError,
    NewConnectionError,
    SSLError,
    TimeoutError,
    InvalidHeader,
    HTTPError
)
from gi.repository import Gtk, GtkSource

from models.response_data import ResponseData
from ui.widgets.request_headers.header_item import HeaderItem
from utils.database import Requests
from utils.misc import get_name_by_type


class RequestHandler:
    def __init__(self, main_window_instance=None):
        self.main_window_instance = main_window_instance
        self.http = urllib3.PoolManager()
        self.list_store = Gtk.ListStore(str, str)
        self.language_manager = GtkSource.LanguageManager.new()
        self.html_lang = self.language_manager.get_language("html")
        self.json_lang = self.language_manager.get_language("json")

    def _get_request_data(self):
        from ui.main_window import app_settings
        selected_row_id = app_settings.get_int('selected-row')
        request = Requests.select(Requests.method, Requests.url).where(Requests.id == selected_row_id).first()
        method = get_name_by_type(self.main_window_instance.request_container.notebook_content.dropdown.get_active() + 1)  # indexed
        body = self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_text(
            self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_start_iter(),
            self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_end_iter(),
            True
        )

        header_items = self.main_window_instance.request_container.pre_request_container.request_headers_container.list_box_headers.get_children()
        headers = [(h.key, h.value) for h in header_items if isinstance(h, HeaderItem)]
        return request, method, body, headers

    def _handle_error(self, error, response_fail):
        error_message = error.args[0] if error.args else "Unknown error"
        print(error_message)
        self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer().set_language(
            self.html_lang)
        self.main_window_instance.request_container.header_status.update_data(response_fail)
        self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer().set_text(
            str(error.args),
            len(str(error.args)))

    def make_request(self, event):
        request, method, body, headers = self._get_request_data()

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

        headers_dict = dict(headers)
        headers_dict["User-Agent"] = str("Saturn/0.0.1")

        headers_dict = {str(k): str(v) for k, v in headers_dict.items()}

        try:
            start_time = time.time()
            resp = self.http.request(
                method=method,
                url=self.main_window_instance.request_container.notebook_content.entry_url.get_text(),
                body=body if method in ["POST", "PUT", "PATCH"] else None,
                headers=headers_dict,
            )

            end_time = time.time()

            elapsed = end_time - start_time
            resp.elapsed = elapsed

            parsed = json.loads(resp.data)

            self.list_store.clear()
            for header in resp.headers:
                self.list_store.append([header, resp.headers[header]])

            self.main_window_instance.request_container.header_status.update_data(resp)

            formatted_json = json.dumps(parsed, indent=8, sort_keys=True)

            self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer().set_language(
                self.json_lang)

            self.main_window_instance.request_container.post_request_container.response_panel.header_response.set_list_store(
                self.list_store)
            self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer().set_text(
                formatted_json)

        except (MaxRetryError, NewConnectionError, SSLError, TimeoutError, InvalidHeader, HTTPError) as e:
            self.main_window_instance.request_container.header_status.update_data(response_fail)
            self._handle_error(e, response_fail)
        except json.JSONDecodeError as e:
            self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer().set_language(
                self.html_lang)
            self.main_window_instance.request_container.header_status.update_data(response_fail)
            self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer().set_text(
                str(e.doc),
                len(str(e.doc)))
