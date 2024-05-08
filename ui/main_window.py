import json

import gi
import urllib3
import time

from utils.database import database, create_needed_tables, RequestModel, Requests
from pydantic import ValidationError


from ui.widgets.query_item import QueryItem
from ui.widgets.query_panel import QueryPanel
from ui.widgets.header_response import HeaderResponse
from ui.widgets.header_status import HeaderStatus
from ui.widgets.source_view import SourceView
from utils.methods import items
from utils.misc import get_type_by_name, get_name_by_type

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Pango, Gio, GLib, GtkSource, GdkPixbuf, Gdk

row_selected = None
json_response = None

buffer = GtkSource.Buffer()
header_response = HeaderResponse()
query_panel = QueryPanel()
app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')


class ProjectList(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.listbox = Gtk.ListBox()
        self.listbox.set_size_request(350, self.listbox.get_height())
        for i in range(5):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
            label = Gtk.Label(label="Projeect " + str(i))
            icon = Gtk.Image.new_from_icon_name("avatar-default")
            hbox.add(icon)
            hbox.add(label)
            row.set_child(hbox)
            self.listbox.add(row)

        self.add(self.listbox)


def show_overlay(data):
    dialog = Gtk.Dialog()
    dialog.set_title(data['title'])
    content_box_dialog = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
    content_box_dialog.set_margin_top(20)
    content_box_dialog.set_margin_start(10)
    content_box_dialog.set_margin_end(10)
    content_box_dialog.set_margin_bottom(20)
    for d in json.loads(data['info']):
        content_box_dialog.add(Gtk.Label(label=d['msg']))

    button = Gtk.Button(label='OK')
    button.set_margin_start(30)
    button.set_margin_end(30)
    button.set_margin_top(20)
    button.connect('clicked', lambda bt: dialog.close())
    content_box_dialog.add(button)
    dialog.set_child(content_box_dialog)
    dialog.set_modal(True)
    dialog.show()


def show_modal(event):
    popover = Gtk.Popover()

    popover_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    entry = Gtk.Entry()
    entry.set_placeholder_text('Request name')

    combo_box = event.get_parent().get_children()[0]
    entry_url = event.get_parent().get_children()[1]

    active = combo_box.get_active()
    selected_text = None
    if active != -1:
        selected_text = combo_box.get_model()[active][0]

    method = selected_text
    url_widget = entry_url

    def store_item(event):

        valida_data = {"name": entry.get_text(), "url": url_widget.get_text(), "type": get_type_by_name(method)}
        try:
            valida_data_model = RequestModel(**valida_data)

            query = (Requests.insert(
                name=valida_data_model.name,
                url=valida_data_model.url,
                type=valida_data_model.type
            ))

            cursor = query.execute()
            if cursor is not None:
                url_widget.set_text("")
                popover.hide()
                request = Requests()
                request.id = cursor
                request.name = valida_data.get("name")
                request.url = valida_data.get("url")
                request.type = valida_data.get("type")

                query_panel.listbox.add(QueryItem(request))

        except ValidationError as e:
            data = {"title": "Atention", "info": e.json()}
            show_overlay(data)

    button = Gtk.Button(label='Save')
    button.connect("clicked", store_item)
    popover_container.add(entry)
    popover_container.add(button)
    popover.add(popover_container)

    #event.set_popover(popover)

    popover.show()


class ResponsePanel(Gtk.Notebook):
    def __init__(self):
        super().__init__()

        label1 = Gtk.Label(label="Response")

        sw = Gtk.ScrolledWindow()

        sw.set_margin_top(5)
        sw.set_margin_bottom(5)
        sw.set_margin_start(5)
        sw.set_margin_end(5)

        source_view = SourceView(buffer, False)
        sw.add(source_view)

        self.append_page(sw, label1)
        self.append_page(header_response, Gtk.Label(label="Headers"))
        self.append_page(Gtk.Label(label="Cookies Tab"), Gtk.Label(label="Cookies"))


def show_open_dialog(self, button):
    self.open_dialog.show()


def open_response(self, dialog, response):
    if response == Gtk.ResponseType.ACCEPT:
        file = dialog.get_file()
        filename = file.get_path()


class MyWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(1600, 1024)

        # set app name
        GLib.set_application_name("Saturn")

        app_settings.connect("changed", query_panel.on_setting_changed)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_panel = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        response_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_panel.set_margin_bottom(5)
        self.add(main_panel)

        self.header_item = None

        self.method_url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.method_url_box.set_margin_start(5)
        self.method_url_box.set_margin_end(5)
        self.entry_url = Gtk.Entry()
        self.entry_url.set_name("entry_url")
        self.entry_url.set_placeholder_text('https://...')
        self.entry_url.set_hexpand(True)
        self.entry_url.set_margin_top(10)
        self.entry_url.set_margin_bottom(0)

        self.box = Gtk.Box()
        self.icon = Gtk.Image(icon_name="list-add-symbolic")
        self.box.add(self.icon)
        self.box.set_tooltip_text('Add request')
        self.add_button = Gtk.Button(child=self.box)
        self.add_button.set_margin_top(10)
        self.add_button.set_margin_bottom(0)
        self.add_button.set_name("add-button")
        self.add_button.connect("clicked", show_modal)

        strings = Gtk.ListStore(str)
        for item in [item["name"] for item in items]:
            strings.append([item])

        self.dropdown = Gtk.ComboBox.new_with_model(model=strings)
        renderer_text = Gtk.CellRendererText()
        self.dropdown.pack_start(renderer_text, True)
        self.dropdown.add_attribute(renderer_text, "text", 0)
        self.dropdown.set_active(0)

        self.dropdown.set_margin_top(10)
        self.dropdown.set_margin_bottom(0)

        self.method_url_box.add(self.dropdown)
        self.method_url_box.add(self.entry_url)
        self.method_url_box.add(self.add_button)
        container_box.add(self.method_url_box)

        query_panel.set_margin_start(5)
        query_panel.set_margin_end(5)

        main_box.add(container_box)
        main_box.add(query_panel)

        response_panel = ResponsePanel()
        response_panel.set_hexpand(True)
        response_panel.set_vexpand(True)

        self.header_status = HeaderStatus(self)

        response_column.add(self.header_status)
        response_column.add(response_panel)
        response_column.set_margin_start(5)
        response_column.set_margin_end(5)

        main_panel.pack1(main_box)
        main_panel.pack2(response_column)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Saturn"
        self.set_titlebar(hb)

        self.popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(Gtk.ModelButton(label="Import Collection"), False, True, 10)
        vbox.pack_start(Gtk.ModelButton(label="Export Collection"), False, True, 10)
        vbox.show_all()
        self.popover.add(vbox)
        self.popover.set_position(Gtk.PositionType.BOTTOM)

        self.open_button = Gtk.MenuButton(popover=self.popover)
        self.open_button.set_tooltip_text("Open Something?")
        hb.pack_start(self.open_button)

        icon = Gio.ThemedIcon(name="document-open-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.open_button.add(image)

        self.open_dialog = Gtk.FileChooserNative.new(title="Choose a file",
                                                     parent=self, action=Gtk.FileChooserAction.OPEN)

    def make_request(self, event):
        request = (Requests
                   .select(Requests.type, Requests.url)
                   .where(Requests.id == app_settings.get_int('selected-row'))
                   .first())
        http = urllib3.PoolManager()
        liststore = Gtk.ListStore(str, str)
        method = get_name_by_type(request.type)

        start_iter = query_panel.sv.get_buffer().get_start_iter()
        end_iter = query_panel.sv.get_buffer().get_end_iter()
        body = query_panel.sv.get_buffer().get_text(start_iter, end_iter, True)

        try:
            start_time = time.time()
            resp = http.request(
                method=get_name_by_type(request.type),
                url=request.url,
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

            header_response.set_list_store(liststore)
            buffer.set_text(formatted_json)

        except urllib3.exceptions.HTTPWarning as e:
            # Handle urllib3 exceptions here
            print("URLError:", e)
            buffer.set_text(str(e.args), len(str(e.args)))
            # Set header even in case of error

        except urllib3.exceptions.HTTPError as e:
            print("HTTPError:", e)
            buffer.set_text(str(e.args), len(str(e.args)))
            # Set header even in case of error

        except Exception as e:
            # Handle other exceptions here
            print("An unexpected error occurred:", e)
            buffer.set_text(str(e.args), len(str(e.args)))
            # Set header even in case of error

        finally:
            # Any cleanup or final actions can go here
            pass

    def show_about(self, action, param):
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)
        self.about.set_modal(self)

        self.about.set_authors(["Douglas Brunal", "Test Data"])
        self.about.set_copyright("Copyright 2024 Douglas Brunal")
        self.about.set_license_type(Gtk.License.GPL_3_0)
        self.about.set_website("http://github.com/frankiity")
        self.about.set_website_label("Github")
        self.about.set_version("1.0")
        # logo = GdkPixbuf.Pixbuf.new_from_file("red_saturn.png")
        self.about.set_logo_icon_name("face-wink")
        # logo_texture = Gdk.Texture.new_for_pixbuf(logo)
        # self.about.set_logo(logo_texture)

        self.about.show()
