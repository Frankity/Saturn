import json
import time

import gi
import urllib3

import src.utils.misc
from src.core.request_handler import RequestHandler
from src.ui.widgets.request_headers.header_item import HeaderItem
from src.utils.database import Requests, Body, Events, Response
from src.utils.misc import items, selected_request, get_domain_name, get_name_by_type

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk


class QueryInput(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.main_window_instance = main_window_instance
        self.request_handler = RequestHandler(main_window_instance)

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
        self.entry_url.connect("activate", self.request_handler.make_request)

        self.box = Gtk.Box(spacing=10)
        self.icon = Gtk.Image(icon_name="document-send-symbolic")
        self.label = Gtk.Label(label="Send")
        self.box.add(self.icon)
        self.box.add(self.label)
        self.box.set_tooltip_text('Send request')

        self.send_button = Gtk.Button(child=self.box)
        self.send_button.set_sensitive(False)
        self.send_button.set_margin_top(5)
        self.send_button.set_size_request(80, 30)
        self.send_button.set_halign(Gtk.Align.CENTER)
        self.send_button.set_margin_bottom(0)
        self.send_button.connect("clicked", self.send_query)

        self.save_box = Gtk.Box()
        self.save_icon = Gtk.Image(icon_name='document-save-symbolic')
        self.save_box.add(self.save_icon)
        self.save_box.set_tooltip_text('Save Request')
        self.save_button = Gtk.Button(child=self.save_box)
        self.save_button.connect('clicked', self.update_request)
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

    async def send_query(self, widget):
        response = await self.some_request_function()  # This should return a response object
        await self._handle_response(response)
        # self.update_request(widget)

    def manage_button(self, event):
        if self.entry_url.get_text() == "":
            self.send_button.set_sensitive(False)
            self.save_button.set_sensitive(False)
        else:
            self.send_button.set_sensitive(True)
            self.save_button.set_sensitive(True)

    def update_request(self, widget):
        selected_row_id = selected_request()

        url = self.entry_url.get_text().strip()
        method = self.dropdown.get_active() + 1

        if selected_row_id == 0:
            result = (Requests
                      .insert(name=get_domain_name(url), url=url, method=method,
                              folder=src.utils.misc.get_current_folder())
                      .execute())
            self.main_window_instance.query_panel.refresh(node_to_expand=None)
        else:
            req = Requests.get(Requests.id == selected_row_id)
            req.url = url
            req.method = method
            req.save()

        event = self.main_window_instance.request_container.pre_request_container.source_view_events.get_buffer().get_text(
            self.main_window_instance.request_container.pre_request_container.source_view_events.get_buffer().get_start_iter(),
            self.main_window_instance.request_container.pre_request_container.source_view_events.get_buffer().get_end_iter(),
            True
        )

        req_event = (Events
                     .select(Events.event)
                     .where(Events.request == selected_request())
                     .first())

        if req_event is None:
            Events.insert(event=event, request=selected_request()).execute()
        else:
            r_event_upd = Events.get(Events.request == selected_request())
            r_event_upd.event = event
            r_event_upd.save()

        # self.main_window_instance.query_panel.refresh()

        body = self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_text(
            self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_start_iter(),
            self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_end_iter(),
            True
        )

        req_body = (Body
                    .select(Body.body)
                    .where(Body.request == selected_request())
                    .first())

        if req_body is None:
            r_body_new = (Body.insert(body=body, request=selected_request()).execute())
            print(r_body_new)
        else:
            r_body_upd = Body.get(Body.request == selected_request())
            r_body_upd.body = body
            r_body_upd.save()

        # self.main_window_instance.query_panel.refresh()

    def _get_request_data(self):
        selected_row_id = selected_request()
        request = Requests.select(Requests.method, Requests.url).where(Requests.id == selected_row_id).first()
        method = get_name_by_type(
            self.main_window_instance.request_container.query_input.dropdown.get_active() + 1)  # indexed
        body = self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_text(
            self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_start_iter(),
            self.main_window_instance.request_container.pre_request_container.sv.get_buffer().get_end_iter(),
            True
        )

        header_items = self.main_window_instance.request_container.pre_request_container.request_headers_container \
            .list_box_headers.get_children()
        headers = [(h.key, h.value) for h in header_items if isinstance(h, HeaderItem)]
        return request, method, body, headers


    def _handle_error(self, sender, error, response_fail):
        error_message = error.args[0] if error.args else "Unknown error"
        print(error_message)
        self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer().set_language(
            self.html_lang)
        self.main_window_instance.request_container.header_status.update_data(response_fail)
        self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer().set_text(
            str(error.args),
            len(str(error.args)))

    async def _handle_response(self, resp):
        # self.list_store.clear()

        response = await resp

        parsed = json.loads(response.data)

        for header in resp.headers:
            self.list_store.append([header, resp.headers[header]])

        self.main_window_instance.request_container.header_status.update_data(resp)

        formatted_json = json.dumps(parsed, indent=8, sort_keys=True)

        self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer() \
            .set_language(self.json_lang)

        self.main_window_instance.request_container.post_request_container.response_panel.header_response \
            .set_list_store(self.list_store)

        self.main_window_instance.request_container.post_request_container.response_panel.source_view.get_buffer() \
            .set_text(formatted_json)

        stored_response = Response.select().where(Response.request == selected_request()).first()

        if Events.select().where(Events.request == selected_request()).count() > 0:
            self.main_window_instance.request_container.pre_request_container.source_view_events.run_events()

        if stored_response:
            existent_response = Response.get(Response.request == selected_request())
            existent_response.body = formatted_json
            existent_response.save()
        else:
            Response.insert(request=selected_request(), body=formatted_json).execute()

