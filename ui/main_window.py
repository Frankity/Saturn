import json

import gi
import urllib3
import time

from ui.widgets.pre_request_container import PreRequestContainer
from ui.widgets.request_container import RequestContainer
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
                type=valida_data_model.method
            ))

            cursor = query.execute()
            if cursor is not None:
                url_widget.set_text("")
                popover.hide()
                request = Requests()
                request.id = cursor
                request.name = valida_data.get("name")
                request.url = valida_data.get("url")
                request.method = valida_data.get("type")

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

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        response_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        main_box.set_size_request(width=300, height=-1)
        main_panel = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        main_panel.set_margin_bottom(5)

        self.add(main_panel)

        self.header_item = None

        query_panel.set_margin_start(5)
        query_panel.set_margin_end(5)

        main_box.add(Gtk.Button(label="collection-name"))

        main_box.add(query_panel)

        request_container = RequestContainer(self)
        app_settings.connect("changed", request_container.on_setting_changed)

        main_panel.pack1(main_box)
        main_panel.pack2(request_container)

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

    def show_about(self, action, param):
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)
        self.about.set_modal(self)

        self.about.set_authors(["Douglas Brunal", "Test Data"])
        self.about.set_copyright("Copyright 2024 Douglas Brunal")
        self.about.set_license_type(Gtk.License.GPL_3_0)
        self.about.set_website("http://github.com/frankiity")
        self.about.set_website_label("Github")
        self.about.set_version("0.0.1")
        # logo = GdkPixbuf.Pixbuf.new_from_file("red_saturn.png")
        self.about.set_logo_icon_name("face-wink")
        # logo_texture = Gdk.Texture.new_for_pixbuf(logo)
        # self.about.set_logo(logo_texture)

        self.about.show()
