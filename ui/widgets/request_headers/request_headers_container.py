import gi

from ui.widgets.request_headers.header_item import HeaderItem

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk


class RequestHeadersContainer(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.header_headers_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.label_header_description = Gtk.Label()
        self.label_header_description.set_xalign(0)
        self.label_header_description.set_hexpand(True)
        self.label_header_description.set_margin_top(0)
        self.label_header_description.set_margin_start(10)
        self.label_header_description.set_markup("<span weight='light' size='large'>HTTP Headers</span>")
        self.header_headers_container.add(self.label_header_description)

        self.list_box_headers = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.list_box_headers.set_margin_top(0)
        self.list_box_headers.set_hexpand(True)

        self.box = Gtk.Box()
        self.icon = Gtk.Image(icon_name="list-add-symbolic")
        self.box.add(self.icon)
        self.box.set_tooltip_text('Add Header')
        self.button = Gtk.Button(child=self.box)
        self.button.set_name("add-button")
        self.button.set_margin_top(10)
        self.button.set_margin_end(10)
        self.button.connect("clicked", lambda button: self.list_box_headers.add(HeaderItem()))
        self.header_headers_container.add(self.button)

        self.list_box_headers.add(self.header_headers_container)
        self.add(self.list_box_headers)
        self.show_all()