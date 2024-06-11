import gi

from src.utils.database import Requests, Folders, Collection
from src.utils.methods import items
from src.utils.misc import selected_request

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class AddCollectionDialog(Gtk.Dialog):
    def __init__(self, main_window_instance=None, modify=False):
        super().__init__(title="Add Collection")

        self.main_window_instance = main_window_instance
        self.set_default_size(350, 70)
        self.set_modal(True)
        self.set_resizable(False)

        name_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        method_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        buttons_box.set_halign(Gtk.Align.CENTER)

        name_box.set_margin_start(5)
        name_box.set_margin_end(5)
        name_box.set_margin_top(5)
        name_box.set_margin_bottom(5)
        buttons_box.set_margin_bottom(5)

        request_name_label = Gtk.Label(label="Name:")
        self.entry_collection_name = Gtk.Entry()
        self.entry_collection_name.set_hexpand(True)

        button_cancel = Gtk.Button(label="Cancel")
        button_save = Gtk.Button(label="Save")

        button_cancel.connect('clicked', lambda x: self.close())
        if modify:
            self.set_title("Modify Request")
            self.get_existing_request_data()
            button_save.connect('clicked', self.update_request)
        else:
            button_save.connect('clicked', self.store_new_collection)

        name_box.add(request_name_label)
        name_box.add(self.entry_collection_name)

        buttons_box.add(button_cancel)
        buttons_box.add(button_save)

        box = self.get_content_area()

        box.add(name_box)
        box.add(method_box)
        box.add(buttons_box)

        self.show_all()

    def get_existing_request_data(self):
        selected_row_id = selected_request()

        req = Requests.select().where(Requests.id == int(selected_row_id)).first()
        if req is not None:
            self.entry_request_name.set_text(req.name)
            self.drop_down_methods.set_active(req.method - 1)

    def update_request(self, widget):

        selected_row_id = selected_request()

        req = Requests.get(Requests.id == selected_row_id)
        req.name = self.entry_request_name.get_text().strip()
        req.method = self.drop_down_methods.get_active() + 1
        req.save()

        self.main_window_instance.query_panel.refresh(self.folder_owner)

        self.close()

    def store_new_collection(self, widget):
        name = self.entry_collection_name.get_text().strip()
        result = (Collection
                  .insert(name=name)
                  .execute())

        self.main_window_instance.refresh_collections()

        self.close()
