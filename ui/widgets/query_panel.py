import gi
from peewee import JOIN

from ui.widgets.query_item import QueryItem
from utils.database import Requests, create_needed_tables, Folders
from utils.misc import get_name_by_type, get_color_by_method

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Gio, Gdk


class QueryPanel(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__()
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)
        self.treestore = Gtk.TreeStore(str, int, int)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search request...")
        self.search_entry.connect("changed", self.on_search_activated)
        self.add(self.search_entry)

        self.search_text = ""

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

        self.add_request_to_list()

    def add_request_to_list(self):

        requests = (Requests
                    .select(Requests,
                            Folders.name.alias('folder_name'),
                            Folders.id.alias('folder_id')
                            )
                    .join(Folders, JOIN.LEFT_OUTER, on=(Requests.folder == Folders.id))
                    .order_by(Folders.id))

        folder_iters = {}

        for row in requests:
            folder_name = row.folders.folder_name
            if folder_name not in folder_iters:
                folder_iter = self.treestore.append(None, [f'<b>{folder_name}</b>', -1, row.folders.folder_id])
                folder_iters[folder_name] = folder_iter
            else:
                folder_iter = folder_iters[folder_name]

            self.treestore.append(folder_iter,
                                  [
                                      f'<b><span color="{get_color_by_method(row.method)}">{get_name_by_type(row.method)}</span></b> {row.name}',
                                      row.id, True])

        self.filtered_model = self.treestore.filter_new()
        self.filtered_model.set_visible_func(self.visible_func)

        self.treeview = Gtk.TreeView(model=self.filtered_model)
        self.treeview.set_headers_visible(False)

        selection = self.treeview.get_selection()
        selection.connect("changed", self.on_tree_selection_changed)
        self.treeview.connect("button-press-event", self.on_button_press_event)

        renderer = Gtk.CellRendererText()
        renderer.set_fixed_size(-1, 40)

        column = Gtk.TreeViewColumn("Paths", renderer, markup=0)

        self.treeview.append_column(column)

        self.scrolled_window.add(self.treeview)
        self.add(self.scrolled_window)

    def on_search_activated(self, event):
        self.search_text = self.search_entry.get_text().lower()
        self.filtered_model.refilter()
        self.expand_matching_nodes()

    def visible_func(self, model, iter, data):
        # Get the current row's value
        value = model[iter][0].lower()

        # Show the row if the search text is empty or the value contains the search text
        if self.search_text in value:
            return True

        # Additionally, show if any of the children match
        if model.iter_has_child(iter):
            child_iter = model.iter_children(iter)
            while child_iter:
                if self.visible_func(model, child_iter, data):
                    return True
                child_iter = model.iter_next(child_iter)

        return False

    def expand_matching_nodes(self):
        # Expand root nodes containing matching rows
        root_iter = self.treestore.get_iter_first()
        path = self.treestore.get_path(root_iter)
        self.treeview.expand_row(path, False)

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')
        if treeiter is not None:
            if model[treeiter][1] > 0:
                value = model[treeiter][1]
                app_settings.set_int('selected-row', value)

    def on_button_press_event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            # Right-click detected, get the path at the click position
            path_info = widget.get_path_at_pos(event.x, event.y)
            if path_info is not None:
                path, column, cell_x, cell_y = path_info
                tree_iter = self.treestore.get_iter(path)
                # Check if the clicked item is a root node (depth == 1)
                if path.get_depth() == 1:
                    self.show_context_menu(event, tree_iter)

    def show_context_menu(self, event, tree_iter):
        menu = Gtk.Menu()

        menu_item_add_folder = Gtk.MenuItem()

        box_menu_add_folder = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_add_folder = Gio.ThemedIcon(name="folder-new-symbolic")
        image_add_folder = Gtk.Image.new_from_gicon(icon_add_folder, Gtk.IconSize.BUTTON)
        label_add_folder = Gtk.Label(label="   Add folder")
        box_menu_add_folder.pack_start(image_add_folder, False, False, 0)
        box_menu_add_folder.pack_start(label_add_folder, False, False, 0)
        menu_item_add_folder.add(box_menu_add_folder)

        menu_item_add_request = Gtk.MenuItem()

        box_menu_add_request = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_add_request = Gio.ThemedIcon(name="bookmark-new-symbolic")
        image_add_request = Gtk.Image.new_from_gicon(icon_add_request, Gtk.IconSize.BUTTON)
        label_add_request = Gtk.Label(label="   Add request")
        box_menu_add_request.pack_start(image_add_request, False, False, 0)
        box_menu_add_request.pack_start(label_add_request, False, False, 0)
        menu_item_add_request.add(box_menu_add_request)

        menu.append(menu_item_add_folder)
        menu.append(menu_item_add_request)

        menu_item_add_folder.connect("activate", self.on_menu_item1_activate, tree_iter)
        menu_item_add_request.connect("activate", self.on_menu_item2_activate, tree_iter)

        menu.show_all()

        menu.popup_at_pointer(event)

    def on_menu_item1_activate(self, widget, tree_iter):
        value = self.treestore[tree_iter][2]
        print(f"Option 1 selected on {value}")

    def on_menu_item2_activate(self, widget, tree_iter):
        value = self.treestore[tree_iter][2]
        print(f"Option 2 selected on {value}")

