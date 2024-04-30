import gi

from models.collection import Collection

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango


class ProjectList(Gtk.Box):

    collections = None
    list_view = Gtk.ListBox()

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.get_collections()

    def get_collections(self):

        # if len(self.list_view) > 0:
        #     self.remove_all_rows()

        collections = Collection.select().order_by(Collection.id)
        self.list_view = Gtk.ListBox()

        for collection in collections:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            box.set_margin_top(10)
            box.set_margin_bottom(10)
            label = Gtk.Label(label=collection.name)
            font_desc = Pango.FontDescription("sans 13")  # Adjust size as needed

            label.set_markup("<span size=\"" + str(int(font_desc.get_size())) + "\">This is my label</span>")
            #label.set_font_map()
            label2 = Gtk.Label(label="gola")
            box.pack_start(label, False, False, 0)
            box.pack_start(label2, False, False, 0)
            list_box_row = Gtk.ListBoxRow()
            list_box_row.add(box)
            self.list_view.add(list_box_row)

            self.add(self.list_view)

    def add_new_collection(self, data):
        if data:
            Collection.insert({
                Collection.name: data
            }).execute()

    def remove_all_rows(self):
        for row in self.list_view:
            self.list_view.remove(row)