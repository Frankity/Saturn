import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import GdkPixbuf, Gtk, Gdk, Pango, Gio, GLib


class HeaderItem(Gtk.Box):
    def __init__(self, key=None, value=None, hid=None, request=None):
        self.key = key
        self.value = value
        self.hid = hid
        self.request = request

        super().__init__()

        self.header_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        self.check_status = Gtk.CheckButton()
        self.check_status.set_active(True)
        self.check_status.connect('toggled', self.on_check_toggled)
        self.set_margin_start(10)
        self.set_margin_top(10)
        self.set_margin_end(10)

        self.entry_key = Gtk.Entry()
        self.entry_key.set_text(self.key if key is not None else "")
        self.entry_key.set_hexpand(True)
        self.entry_key.set_placeholder_text('eg: Authorization')
        self.entry_key.connect("changed", self.set_key_text)
        self.entry_value = Gtk.Entry()
        self.entry_value.set_text(self.value if value is not None else "")
        self.entry_value.set_hexpand(True)
        self.entry_value.set_placeholder_text('eg: Bearer ...')
        self.entry_value.connect("changed", self.set_value_text)

        self.box = Gtk.Box()
        self.icon = Gtk.Image(icon_name="edit-delete-symbolic")

        self.box.add(self.icon)

        self.box.set_tooltip_text('Delete')
        self.button = Gtk.Button(child=self.box)
        self.button.set_name("delete-button")
        self.button.connect("clicked", self.remove_me)

        self.header_container.add(self.check_status)
        self.header_container.add(self.entry_key)
        self.header_container.add(self.entry_value)
        self.header_container.add(self.button)
        self.add(self.header_container)
        self.show_all()

    def set_key_text(self, event):
        self.key = event.get_text()

    def set_value_text(self, event):
        self.value = event.get_text()

    def on_check_toggled(self, check):
        if check.props.active:
            self.entry_key.set_sensitive(True)
            self.entry_value.set_sensitive(True)
            self.button.set_sensitive(True)
        else:
            self.entry_key.set_sensitive(False)
            self.entry_value.set_sensitive(False)
            self.button.set_sensitive(False)

    def remove_me(self, button):
        parent = self.get_parent()
        if parent is not None:
            parent.remove(self)
