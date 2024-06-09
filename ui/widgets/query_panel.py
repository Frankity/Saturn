import gi
from peewee import JOIN

from ui.dialogs.add_request_dialog import AddRequestDialog
from ui.dialogs.yes_no_dialog import YesNoDialog
from ui.widgets.query_item import QueryItem
from utils.database import Requests, create_needed_tables, Folders, Body, Params, Headers
from utils.misc import get_name_by_type, get_color_by_method, selected_request

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Gio, Gdk


class QueryPanel(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__()

        self.treeview = Gtk.TreeView()
        self.main_window_instance = main_window_instance
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)
        self.treestore = Gtk.TreeStore(str, int, int)  # name,request_id,folder_id

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search request...")
        self.search_entry.connect("changed", self.on_search_activated)
        self.add(self.search_entry)

        self.search_text = ""
        self.initiate = False  # check for first added

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.add(self.scrolled_window)

        self.update_model()
        self.add_request_to_list()

    def update_model(self):

        self.treestore.clear()

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

    def add_request_to_list(self):

        self.filtered_model = self.treestore.filter_new()
        self.filtered_model.set_visible_func(self.visible_func)

        self.treeview.set_model(self.filtered_model)
        self.treeview.set_headers_visible(False)

        selection = self.treeview.get_selection()
        selection.connect("changed", self.on_tree_selection_changed)
        self.treeview.connect("button-press-event", self.on_button_press_event)

        renderer = Gtk.CellRendererText()
        renderer.set_fixed_size(-1, 30)

        column = Gtk.TreeViewColumn("Paths", renderer, markup=0)

        if not self.initiate:
            self.treeview.append_column(column)
            self.scrolled_window.add(self.treeview)

        self.initiate = True

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
                    self.show_context_menu_over_folder(event, tree_iter)
                else:
                    self.show_context_menu_over_request(event, tree_iter)

    def show_context_menu_over_folder(self, event, tree_iter):
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

    def show_context_menu_over_request(self, event, tree_iter):
        menu = Gtk.Menu()

        menu_item_add_folder = Gtk.MenuItem()
        box_menu_add_folder = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_add_folder = Gio.ThemedIcon(name="document-edit-symbolic")
        image_add_folder = Gtk.Image.new_from_gicon(icon_add_folder, Gtk.IconSize.BUTTON)
        label_add_folder = Gtk.Label(label="   Modify")
        box_menu_add_folder.pack_start(image_add_folder, False, False, 0)
        box_menu_add_folder.pack_start(label_add_folder, False, False, 0)
        menu_item_add_folder.add(box_menu_add_folder)

        menu_item_add_request = Gtk.MenuItem()
        box_menu_add_request = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_add_request = Gio.ThemedIcon(name="edit-delete-symbolic")
        image_add_request = Gtk.Image.new_from_gicon(icon_add_request, Gtk.IconSize.BUTTON)
        label_add_request = Gtk.Label(label="   Delete")
        box_menu_add_request.pack_start(image_add_request, False, False, 0)
        box_menu_add_request.pack_start(label_add_request, False, False, 0)
        menu_item_add_request.add(box_menu_add_request)

        menu.append(menu_item_add_folder)
        menu.append(menu_item_add_request)

        menu_item_add_folder.connect("activate", self.on_request_item1_activate, tree_iter)
        menu_item_add_request.connect("activate", self.on_request_item2_activate, tree_iter)

        menu.show_all()
        menu.popup_at_pointer(event)

    def on_menu_item1_activate(self, widget, tree_iter):
        value = self.treestore[tree_iter][2]
        print(f"Option 1 selected on {value}")

    def on_menu_item2_activate(self, widget, tree_iter):
        folder_id = self.treestore[tree_iter][2]
        add_request_dialog = AddRequestDialog(folder_owner=folder_id,
                                              main_window_instance=self.main_window_instance)
        add_request_dialog.show()

    def on_request_item1_activate(self, widget, tree_iter):
        folder_id = self.treestore[tree_iter][2]
        add_request_dialog = AddRequestDialog(folder_owner=folder_id,
                                              main_window_instance=self.main_window_instance, modify=True)
        add_request_dialog.show()

    def on_request_item2_activate(self, widget, tree_iter):
        dialog = YesNoDialog(self.main_window_instance,
                             title="Delete Request",
                             message="Are you sure about deleting this request?",
                             )
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            #request
            req = Requests.get(Requests.id == int(selected_request()))
            folder_id = req.folder
            req.delete_instance()

            #body
            e_body = (Body.select().where(Body.request == int(selected_request()))).first()
            if e_body is not None:
                body = Body.get(Body.request == int(selected_request()))
                body.delete_instance()

            #params
            e_params = (Params.select().where(Params.request == int(selected_request()))).first()
            if e_params is not None:
                param = Params.get(Params.request == int(selected_request()))
                param.delete_instance()

            #headers
            e_headers = (Headers.select().where(Headers.request == int(selected_request()))).first()
            if e_headers is not None:
                headers = Headers.get(Headers.request == int(selected_request()))
                headers.delete_instance()

            self.refresh(node_to_expand=int(folder_id))

        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()

    def expand_specific_node(self, node_id):
        it = self.treestore.get_iter_first()
        while it is not None:
            if self.treestore[it][2] == node_id:
                path = self.treestore.get_path(it)
                self.treeview.expand_row(path, True)
            it = self.treestore.iter_next(it)

    def refresh(self, node_to_expand=None):
        self.update_model()
        if node_to_expand:
            self.expand_specific_node(node_to_expand)
