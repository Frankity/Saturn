import json
import time
import urllib3
from urllib3.util.retry import Retry
from urllib3.exceptions import (
    MaxRetryError,
    NewConnectionError,
    SSLError,
    TimeoutError,
    InvalidHeader,
    HTTPError
)
from gi.repository import Gtk, GtkSource

from src.models.response_data import ResponseData
from src.ui.widgets.request_headers.header_item import HeaderItem
from src.utils.database import Requests, Response, Events
from src.utils.misc import get_name_by_type, selected_request


class RequestHandler:
    def __init__(self, main_window_instance=None):
        self.main_window_instance = main_window_instance

        retry_strategy = Retry(
            total=1,  # Máximo de 3 reintentos
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE", "PATCH"]
        )
        self.http = urllib3.PoolManager(retries=retry_strategy)

        # self.list_store = Gtk.ListStore(str, str)
        # self.language_manager = GtkSource.LanguageManager.new()
        # self.html_lang = self.language_manager.get_language("html")
        # self.json_lang = self.language_manager.get_language("json")

    async def make_request(self, request_data):
        request, method, body, headers = request_data

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
                url=self.main_window_instance.request_container.query_input.entry_url.get_text(),
                body=body if method in ["POST", "PUT", "PATCH"] else None,
                headers=headers_dict,
                timeout=5.0  # Añadiendo timeout de 5 segundos
            )

            end_time = time.time()

            elapsed = end_time - start_time
            resp.elapsed = elapsed

            return resp.data, resp.headers, resp.elapsed
        except (MaxRetryError, NewConnectionError, SSLError, TimeoutError, InvalidHeader, HTTPError) as e:
            print(e)

            #
            # self.main_window_instance.request_container.header_status.update_data(response_fail)
            # self._handle_error(e, response_fail)
        except json.JSONDecodeError as e:
            print(e)
            # self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer() \
            #     .set_language(
            #     self.html_lang)
            # self.main_window_instance.request_container.header_status.update_data(response_fail)
            # self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer() \
            #     .set_text(
            #     str(e.doc),
            #     len(str(e.doc)))
