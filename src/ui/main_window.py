import json

import gi

import src.utils.misc
from src.ui.widgets.query_panel import QueryPanel
from src.ui.widgets.request_container import RequestContainer

from src.ui.widgets.header_response import HeaderResponse
from src.utils.database import Collection

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Gio, GLib, GtkSource
from src.ui.dialogs.add_collection_dialog import AddCollectionDialog

row_selected = None
json_response = None

buffer = GtkSource.Buffer()
header_response = HeaderResponse()
app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')


def show_open_dialog(self, button):
    self.open_dialog.show()


def open_response(self, dialog, response):
    if response == Gtk.ResponseType.ACCEPT:
        file = dialog.get_file()
        filename = file.get_path()


class AppWindow(Gtk.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(1600, 1024)

        self.collections_list_store = Gtk.ListStore(str, int)

        # set app name
        GLib.set_application_name("Saturn")

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        collection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        main_box.set_size_request(width=300, height=-1)
        main_panel = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        main_panel.set_margin_bottom(5)

        self.add(main_panel)

        self.header_item = None

        self.query_panel = QueryPanel(self)

        self.query_panel.set_margin_start(5)
        self.query_panel.set_margin_end(5)

        self.collection_dropdown = Gtk.ComboBox()
        self.collection_dropdown.set_hexpand(True)

        self.box = Gtk.Box(spacing=0)
        self.icon = Gtk.Image(icon_name="view-more-symbolic")
        self.box.add(self.icon)
        self.box.set_tooltip_text('Menu')
        self.menu_button = Gtk.Button(child=self.box)
        self.menu_button.connect('clicked', self.show_add_collelction_dialog)

        collection_box.set_margin_top(5)
        collection_box.set_margin_bottom(5)
        collection_box.set_margin_start(5)
        collection_box.set_margin_end(5)

        self.collection_dropdown.connect("changed", self.on_combo_changed)

        collection_box.add(self.collection_dropdown)
        collection_box.add(self.menu_button)

        collection_box.set_tooltip_text("Manage Collections")

        main_box.add(collection_box)

        main_box.add(self.query_panel)

        self.request_container = RequestContainer(self)
        app_settings.connect("changed", self.request_container.on_setting_changed)

        main_panel.pack1(main_box, shrink=False)
        main_panel.pack2(self.request_container, resize=True, shrink=False)

        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)

        switch = Gtk.Switch()
        switch.connect("notify::active", self.on_switch_activated)
        switch.set_active(False)
        hb.pack_end(switch)

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

        self.get_collections()

    def on_switch_activated(self, switch, gparam):
        if switch.get_active():
            state = "on"
            self.request_container.post_request_container.response_panel.source_view.set_wrap_mode(True)
        else:
            self.request_container.post_request_container.response_panel.source_view.set_wrap_mode(False)
            state = "off"
        print("Switch was turned", state)

    def show_add_collelction_dialog(self, event):
        add_collection_dialog = AddCollectionDialog(main_window_instance=self, modify=False)
        add_collection_dialog.show()

    def on_combo_changed(self, widget):
        active_iter = widget.get_active_iter()
        if active_iter:
            active_text = widget.get_model()[active_iter][0]
            active_integer = widget.get_model()[active_iter][1]
            src.utils.misc.set_current_collection(active_integer)
            self.query_panel.update_model()

    def get_collections(self):
        self.collections_list_store.clear()

        for col in Collection.select():
            self.collections_list_store.append([col.name, col.id])

        self.collection_dropdown.set_model(self.collections_list_store)
        renderer_text = Gtk.CellRendererText()
        self.collection_dropdown.pack_start(renderer_text, True)
        self.collection_dropdown.add_attribute(renderer_text, "text", 0)
        self.collection_dropdown.set_active(0)

    def refresh_collections(self):
        self.collections_list_store.clear()

        for col in Collection.select():
            self.collections_list_store.append([col.name, col.id])

        self.collection_dropdown.set_active(0)

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
