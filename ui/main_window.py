import gi

from models.requests import Requests
from res.methods import items
from ui.widgets.header_item import HeaderItem
from ui.widgets.request_window import RequestWindow

gi.require_version('Gtk', '4.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gtk, Gdk, Pango, Gio, GLib


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
            hbox.append(icon)
            hbox.append(label)
            row.set_child(hbox)
            self.listbox.append(row)

        self.append(self.listbox)


def show_modal(event):
    popover = Gtk.Popover()

    popover_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
    entry = Gtk.Entry()
    entry.set_placeholder_text('Request name')

    method = event.get_parent().get_first_child().props.selected_item.props.string
    url_widget = event.get_parent().get_last_child().get_prev_sibling()

    def store_item(event):
        print("test")
        query = (Requests.insert(
            name=entry.get_text(),
            url=url_widget.get_text(),
            type=get_type_by_name(method)
        ))
        cursor = query.execute()
        if cursor is not None:
            url_widget.set_text("")
            popover.hide()

    button = Gtk.Button(label='Save')
    button.connect("clicked", store_item)
    popover_container.append(entry)
    popover_container.append(button)
    popover.set_child(popover_container)
    popover.set_parent(event)

    popover.show()


def get_type_by_name(name):
    for item in items:
        if item["name"].lower() == name.lower():
            return item["type"]
    return None


def get_name_by_type(tpe):
    for item in items:
        if item["type"] == tpe:
            return item["name"]
    return None


class QueryPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        self.header_item = None

        self.listbox = Gtk.ListBox()
        self.listbox.set_size_request(300, self.listbox.get_height())

        font_desc = Pango.FontDescription("sans 12")

        self.container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.method_url_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        self.entry_url = Gtk.Entry()
        self.entry_url.set_name("entry_url")
        self.entry_url.set_placeholder_text('https://...')
        self.entry_url.set_hexpand(True)
        self.entry_url.set_margin_top(10)
        self.entry_url.set_margin_bottom(10)

        self.box = Gtk.Box()
        self.icon = Gtk.Image(icon_name="list-add-symbolic")
        self.box.append(self.icon)
        self.box.set_tooltip_text('Add request')
        self.add_button = Gtk.Button(child=self.box)
        self.add_button.set_margin_top(10)
        self.add_button.set_margin_bottom(10)
        self.add_button.set_name("add-button")
        self.add_button.connect("clicked", show_modal)

        self.dropdown = Gtk.DropDown()
        self.dropdown.set_margin_top(10)
        self.dropdown.set_margin_bottom(10)
        # dropdown.connect('notify::selected-item', self.on_string_selected)

        strings = Gtk.StringList()
        self.dropdown.props.model = strings

        for item in [item["name"] for item in items]:
            strings.append(item)
        self.method_url_box.append(self.dropdown)
        self.method_url_box.append(self.entry_url)
        self.method_url_box.append(self.add_button)
        self.container_box.append(self.method_url_box)

        self.header_headers_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.label_header_description = Gtk.Label()
        self.label_header_description.set_xalign(0)
        self.label_header_description.set_hexpand(True)
        self.label_header_description.set_margin_top(0)
        self.label_header_description.set_margin_start(10)
        self.label_header_description.set_markup("<span weight='light' size='large'>HTTP Headers</span>")
        self.header_headers_container.append(self.label_header_description)

        self.list_box_headers = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.list_box_headers.set_margin_top(5)
        self.list_box_headers.set_hexpand(True)

        self.box = Gtk.Box()
        self.icon = Gtk.Image(icon_name="list-add-symbolic")
        self.box.append(self.icon)
        self.box.set_tooltip_text('Add Header')
        self.button = Gtk.Button(child=self.box)
        self.button.set_name("add-button")
        self.button.set_margin_top(10)
        self.button.set_margin_end(10)
        self.button.connect("clicked", lambda button: self.list_box_headers.append(HeaderItem()))
        self.header_headers_container.append(self.button)

        self.list_box_headers.append(self.header_headers_container)

        self.options_query = Gtk.Notebook()
        self.options_query.set_vexpand(True)
        self.options_query.append_page(self.listbox, Gtk.Label(label="Query"))
        self.options_query.append_page(self.list_box_headers, Gtk.Label(label="Headers"))
        self.options_query.append_page(Gtk.Label(label="Auth"), Gtk.Label(label="Auth"))
        self.options_query.append_page(Gtk.Label(label="Body"), Gtk.Label(label="Body"))
        self.options_query.append_page(Gtk.Label(label="Events"), Gtk.Label(label="Event"))

        self.container_box.append(self.options_query)

        def show_menu(widget, event):
            # print(event)
            # print(widget)
            # if event == Gdk.EventType.BUTTON_PRESS:
            # print(event.get_child().get_child().get_name())
            print(":asdasd")
            # menu_model = Gio.Menu()
            #
            # item1 = Gio.MenuItem.new("Item 1", "app.item1")
            # menu_model.append_item(item1)
            # item2 = Gio.MenuItem.new("Item 2", "app.item2")
            # menu_model.append_item(item2)
            #
            # menu = Gtk.PopoverMenu.new_from_model(menu_model)
            # menu.props.position = Gtk.PositionType.RIGHT
            #
            # menu.set_parent(event)
            # menu.show()

        self.listbox.connect("row-selected", show_menu)

        requests = Requests.select()

        for element in requests:
            row = Gtk.ListBoxRow()
            row.set_name("rbox")
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)  # lista
            hbox.set_name("hbox")
            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)  # filas
            hbox.set_name("vbox")
            item_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            hbox.set_name("ibox")
            vbox.set_hexpand(True)

            label_title = Gtk.Label()
            label_title.set_markup(
                "<span size=\"" + str(int(font_desc.get_size())) + "\"><b>" + element.name + "</b></span>")
            label_title.set_justify(Gtk.Justification.LEFT)
            label_title.set_margin_start(10)
            label_title.set_margin_top(10)
            label_title.set_xalign(0)

            label_subtitle = Gtk.Label()
            label_subtitle.set_markup(
                "<span weight='light' color='#dddddd' size='medium'>" + element.url + "</span>")
            label_subtitle.set_margin_start(10)
            label_subtitle.set_margin_bottom(10)
            label_subtitle.set_xalign(0)
            label_subtitle.set_justify(Gtk.Justification.LEFT)

            label_type = Gtk.Label()
            label_type.set_markup("<span color='#ffffff' size='medium'>   " + get_name_by_type(element.type) + "   </span>")
            label_type.set_name(get_type_color_label(element.type))
            label_type.set_xalign(2)
            label_type.set_margin_end(10)
            label_type.set_margin_top(17)
            label_type.set_margin_bottom(17)
            label_type.set_hexpand(False)
            label_type.set_vexpand(False)

            item_box.append(label_title)
            item_box.append(label_subtitle)

            vbox.append(item_box)
            hbox.append(vbox)
            item_box.set_halign(Gtk.Align.START)

            hbox.append(label_type)

            row.set_child(hbox)

            self.listbox.append(row)

        self.append(self.container_box)


def get_type_color_label(tpe):
    if tpe == 1:
        return 'type-get-label'
    elif tpe == 2:
        return 'type-post-label'
    elif tpe == 4:
        return 'type-delete-label'

class ResponsePanel(Gtk.Notebook):
    def __init__(self):
        super().__init__()

        label1 = Gtk.Label(label="Response")
        self.append_page(Gtk.Label(label="Response Tab"), label1)

        label2 = Gtk.Label(label="Headers")
        self.append_page(Gtk.Label(label="Headers Tab"), label2)

        label3 = Gtk.Label(label="Cookies")
        self.append_page(Gtk.Label(label="Cookies Tab"), label3)


def show_open_dialog(self, button):
    self.open_dialog.show()


def open_response(self, dialog, response):
    if response == Gtk.ResponseType.ACCEPT:
        file = dialog.get_file()
        filename = file.get_path()
        print(filename)


class StatusHeader(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.set_margin_top(20)
        self.set_margin_bottom(15)
        self.set_margin_start(10)
        label_status = Gtk.Label()
        label_status.set_markup("<span weight='light' size='medium'>Status: </span><span weight='bold' "
                                "color='#008800'>200 OK</span>")
        label_size = Gtk.Label()
        label_size.set_markup("<span weight='light' size='medium'>Size: </span><span weight='bold' "
                              "color='#008800'>220 Bytes</span>")
        label_time = Gtk.Label()
        label_time.set_markup("<span weight='light' size='medium'>Time: </span><span weight='bold' "
                              "color='#008800'>299 ms</span>")

        box = Gtk.Box(spacing=6)
        icon = Gtk.Image(icon_name="system-run-symbolic")
        label = Gtk.Label(label="Run")
        box.append(icon)
        box.append(label)
        button = Gtk.Button(child=box)
        button.set_halign(Gtk.Align.END)
        button.set_margin_end(10)
        button.set_hexpand(True)  # trick to righth align

        self.append(label_status)
        self.append(label_size)
        self.append(label_time)
        self.append(button)


class MyWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_default_size(1600, 1024)

        self.set_title("Saturn")
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        main_panel = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        response_column = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_panel.set_margin_bottom(5)
        self.set_child(main_panel)

        query_panel = QueryPanel()
        query_panel.set_margin_start(5)
        query_panel.set_margin_end(5)
        main_box.append(query_panel)

        response_panel = ResponsePanel()
        response_panel.set_hexpand(True)
        response_panel.set_vexpand(True)

        response_column.append(StatusHeader())
        response_column.append(response_panel)
        response_column.set_margin_start(5)
        response_column.set_margin_end(5)

        main_panel.set_start_child(main_box)
        main_panel.set_end_child(response_column)

        self.header = Gtk.HeaderBar()

        self.set_titlebar(self.header)
        self.open_button = Gtk.Button(label="Open")
        self.header.pack_start(self.open_button)

        self.open_button.set_icon_name("document-open-symbolic")

        self.open_dialog = Gtk.FileChooserNative.new(title="Choose a file",
                                                     parent=self, action=Gtk.FileChooserAction.OPEN)

        self.open_dialog.connect("response", open_response)
        self.open_button.connect("clicked", show_open_dialog)

        # Create a new "Action"
        action = Gio.SimpleAction.new("something", None)
        # action.connect("activate", self.print_something)
        self.add_action(action)  # Here the action is being added to the window, but you could add it to the
        # application or an "ActionGroup"

        # Create a new menu, containing that action
        menu = Gio.Menu.new()
        menu.append("Do Something", "win.something")  # Or you would do app.grape if you had attached the
        # action to the application

        # Create a popover
        self.popover = Gtk.PopoverMenu()  # Create a new popover menu
        self.popover.set_menu_model(menu)

        # Create a menu button
        self.hamburger = Gtk.MenuButton()
        self.hamburger.set_popover(self.popover)
        self.hamburger.set_icon_name("open-menu-symbolic")  # Give it a nice icon

        # Add menu button to the header bar
        self.header.pack_start(self.hamburger)

        # set app name
        GLib.set_application_name("Saturn")

        # Add an about dialog
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.show_about)
        self.add_action(action)  # Here the action is being added to the window, but you could add it to the
        menu.append("About", "win.about")

    def show_about(self, action, param):
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)
        self.about.set_modal(self)

        self.about.set_authors(["Douglas Brunal", "Test Data"])
        self.about.set_copyright("Copyright 2024 Douglas Brunal")
        self.about.set_license_type(Gtk.License.GPL_3_0)
        self.about.set_website("http://example.com")
        self.about.set_website_label("My Website")
        self.about.set_version("1.0")
        self.about.set_logo_icon_name("face-wink")

        self.about.show()
