import gi

from utils.database import Params

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk


class ParamItem(Gtk.Box):
    def __init__(self, key=None, value=None, hid=None, request=None, enabled=None):
        self.key = key
        self.value = value
        self.hid = hid
        self.request = request
        self.enabled = enabled

        super().__init__()

        self.params_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        self.check_status = Gtk.CheckButton()
        self.check_status.connect('toggled', self.on_check_toggled)
        self.set_margin_start(10)
        self.set_margin_top(10)
        self.set_margin_end(10)

        self.entry_key = Gtk.Entry()
        self.entry_key.set_text(self.key if key is not None else "")
        self.entry_key.set_hexpand(True)
        self.entry_key.set_placeholder_text('eg: id')
        self.entry_key.connect("changed", self.set_key_text)
        self.entry_value = Gtk.Entry()
        self.entry_value.set_text(self.value if value is not None else "")
        self.entry_value.set_hexpand(True)
        self.entry_value.set_placeholder_text('eg: 255')
        self.entry_value.connect("changed", self.set_value_text)

        self.box = Gtk.Box()
        self.icon = Gtk.Image(icon_name="edit-delete-symbolic")

        self.box.add(self.icon)

        self.box.set_tooltip_text('Delete')
        self.button = Gtk.Button(child=self.box)
        self.button.set_name("delete-button")
        self.button.connect("clicked", self.remove_me)

        self.params_container.add(self.check_status)
        self.params_container.add(self.entry_key)
        self.params_container.add(self.entry_value)
        self.params_container.add(self.button)
        self.add(self.params_container)

        if self.hid is None:
            self.hid = self.save_to_database()

        if self.enabled:
            self.check_status.set_active(True)
            self.entry_key.set_sensitive(True)
            self.entry_value.set_sensitive(True)
            self.button.set_sensitive(True)
        else:
            self.check_status.set_active(False)
            self.entry_key.set_sensitive(False)
            self.entry_value.set_sensitive(False)
            self.button.set_sensitive(False)

        self.show_all()

    def save_to_database(self):
        from ui.main_window import app_settings
        selected_row_id = app_settings.get_int('selected-row')
        result = (Params
                  .insert(key='', value='', request=selected_row_id)
                  .execute())
        return result

    def set_key_text(self, event):
        self.key = event.get_text()
        param = Params.get(Params.id == self.hid)
        param.key = self.key
        param.save()

    def set_value_text(self, event):
        self.value = event.get_text()
        param = Params.get(Params.id == self.hid)
        param.value = self.value
        param.save()

    def on_check_toggled(self, check):
        param = Params.get(Params.id == self.hid)
        if check.props.active:
            param.enabled = True
            self.entry_key.set_sensitive(True)
            self.entry_value.set_sensitive(True)
            self.button.set_sensitive(True)
        else:
            param.enabled = False
            self.entry_key.set_sensitive(False)
            self.entry_value.set_sensitive(False)
            self.button.set_sensitive(False)
        param.save()

    def remove_me(self, button):
        Params.delete().where(Params.id == self.hid).execute()
        parent = self.get_parent()
        if parent is not None:
            parent.remove(self)
