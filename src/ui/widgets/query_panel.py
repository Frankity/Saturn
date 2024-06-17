import gi
import peewee

import src.utils.misc
from src.ui.dialogs.add_request_dialog import AddRequestDialog
from src.ui.dialogs.add_folder_dialog import AddFolderDialog
from src.ui.dialogs.yes_no_dialog import YesNoDialog
from src.utils.database import Requests, create_needed_tables, Folders, Body, Params, Headers
from src.utils.misc import get_name_by_type, get_color_by_method, selected_request, get_current_collection

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Gio, Gdk


class QueryPanel(Gtk.Box):
    def __init__(self, main_window_instance=None):
        super().__init__()

        self.collection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        self.treeview = Gtk.TreeView()
        self.main_window_instance = main_window_instance
        self.set_orientation(Gtk.Orientation.VERTICAL)
        self.set_spacing(5)
        self.treestore = Gtk.TreeStore(str, int, int, str)  # name, request_id, folder_id, icon_name

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search request...")
        self.search_entry.connect("changed", self.on_search_activated)
        self.search_entry.set_hexpand(True)

        self.box = Gtk.Box(spacing=0)
        self.icon = Gtk.Image(icon_name="list-add-symbolic")
        self.box.add(self.icon)
        self.box.set_tooltip_text('Add')
        self.menu_button = Gtk.Button(child=self.box)
        self.menu_button.connect('clicked', self.show_context_menu_over_folder)

        self.collection_box.add(self.search_entry)
        self.collection_box.add(self.menu_button)

        self.add(self.collection_box)

        self.search_text = ""
        self.initiate = False  # check for first added
        self.folder_iter = None

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.add(self.scrolled_window)

        self.add_request_to_list()

    def update_model(self):

        self.treestore.clear()

        folders = (Folders.select().where(Folders.collection == get_current_collection()))  # add environment check
        requests = (Requests.select().where(Requests.collection == get_current_collection()))

        folder_iters = {}

        try:
            for row in folders:
                folder_name = row.name
                if folder_name not in folder_iters:
                    self.folder_iter = self.treestore.append(None, [f' <b>{folder_name}</b>', -1, row.id, "folder"
                                                                                                          "-symbolic"])
                    folder_iters[folder_name] = self.folder_iter
                else:
                    self.folder_iter = folder_iters[folder_name]

                req_filter = [reqs for reqs in requests if int(reqs.folder) == int(row.id)]
                for req in req_filter:
                    self.treestore.append(self.folder_iter,
                                          [f'<b>  <span color="{get_color_by_method(req.method)}">'
                                           f'{get_name_by_type(req.method)}</span></b> {req.name}',
                                           req.id, True, 'network-transmit-symbolic'])
            no_folder_request = [reqs for reqs in requests if int(reqs.folder) == 0]

            for req in no_folder_request:
                self.treestore.append(None,
                                      [f'<b>  <span color="{get_color_by_method(req.method)}">'
                                       f'{get_name_by_type(req.method)}</span></b> {req.name}',
                                       req.id, True, 'network-transmit-symbolic'])

            if len(folder_iters) != 0:
                src.utils.misc.set_current_folder(self.treestore[self.folder_iter][2])

        except peewee.OperationalError as e:
            create_needed_tables()

    def add_request_to_list(self):

        self.filtered_model = self.treestore.filter_new()
        self.filtered_model.set_visible_func(self.visible_func)

        self.treeview.set_model(self.filtered_model)
        self.treeview.set_headers_visible(False)

        selection = self.treeview.get_selection()
        selection.connect("changed", self.on_tree_selection_changed)
        self.treeview.connect("button-press-event", self.on_button_press_event)

        icon_renderer = Gtk.CellRendererPixbuf()
        text_renderer = Gtk.CellRendererText()
        text_renderer.set_fixed_size(-1, 35)

        column = Gtk.TreeViewColumn("Paths")
        column.pack_start(icon_renderer, False)
        column.pack_start(text_renderer, True)

        column.add_attribute(icon_renderer, "icon-name", 3)
        column.add_attribute(text_renderer, "markup", 0)

        if not self.initiate:
            self.treeview.append_column(column)
            self.scrolled_window.add(self.treeview)

        self.treeview.connect("row-expanded", self.on_row_expanded)
        self.treeview.connect("row-collapsed", self.on_row_collapsed)

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
                if self.treestore[tree_iter][3] == 'network-transmit-symbolic':  # as we use the same menu, we don't
                    # want to show the folder menu over requests without folders
                    self.show_context_menu_over_request(event, tree_iter)
                else:
                    self.show_context_menu_over_folder(event, tree_iter)

        # if event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS:
        #     # Double-click detected
        #     path_info = self.treeview.get_path_at_pos(event.x, event.y)
        #     if path_info is not None:
        #         path, column, cell_x, cell_y = path_info
        #         model = self.treeview.get_model()
        #         tree_iter = model.get_iter(path)
        #         app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')
        #         app_settings.set_int('selected-row', model.get_value(tree_iter, 1))

    def show_context_menu_over_folder(self, event, tree_iter=None):
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
        menu.show_all()

        if tree_iter is not None:
            menu_item_add_folder.connect("activate", self.on_menu_item1_activate, tree_iter)
            menu_item_add_request.connect("activate", self.on_menu_item2_activate, tree_iter)
            menu.popup_at_pointer(event)
        else:
            menu_item_add_folder.connect("activate", self.on_menu_item1_activate, tree_iter)
            menu_item_add_request.connect("activate", self.on_menu_item2_activate, tree_iter)
            menu.popup_at_widget(event, Gdk.Gravity.SOUTH_EAST, Gdk.Gravity.NORTH_WEST)

    def show_context_menu_over_request(self, event, tree_iter):
        menu = Gtk.Menu()

        menu_item_modify_request = Gtk.MenuItem()
        box_menu_add_folder = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_add_folder = Gio.ThemedIcon(name="document-edit-symbolic")
        image_add_folder = Gtk.Image.new_from_gicon(icon_add_folder, Gtk.IconSize.BUTTON)
        label_remove_request = Gtk.Label()
        label_remove_request.set_markup('<span weight="light">   Modify</span>')

        box_menu_add_folder.pack_start(image_add_folder, False, False, 0)
        box_menu_add_folder.pack_start(label_remove_request, False, False, 0)
        menu_item_modify_request.add(box_menu_add_folder)

        menu_item_add_request = Gtk.MenuItem()
        box_menu_add_request = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        icon_add_request = Gio.ThemedIcon(name="edit-delete-symbolic")
        image_add_request = Gtk.Image.new_from_gicon(icon_add_request, Gtk.IconSize.BUTTON)
        label_delete_request = Gtk.Label()
        label_delete_request.set_markup('<span weight="light" color="#ff0000">   Delete</span>')

        box_menu_add_request.pack_start(image_add_request, False, False, 0)
        box_menu_add_request.pack_start(label_delete_request, False, False, 0)
        menu_item_add_request.add(box_menu_add_request)

        menu.append(menu_item_modify_request)
        menu.append(menu_item_add_request)

        menu_item_modify_request.connect("activate", self.on_request_item1_activate, tree_iter)
        menu_item_add_request.connect("activate", self.on_request_item2_activate, tree_iter)

        menu.show_all()
        menu.popup_at_pointer(event)

    def on_menu_item1_activate(self, widget, tree_iter=None):
        if tree_iter is not None:
            print("aaaa")
        else:
            add_folder_dialog = AddFolderDialog(folder_owner=None,
                                                main_window_instance=self.main_window_instance)
            add_folder_dialog.show()

    def on_menu_item2_activate(self, widget, tree_iter=None):
        if tree_iter is not None:
            self.folder_id = self.treestore[tree_iter][2] if self.treestore[tree_iter][2] > 0 else 0
        else:
            self.folder_id = 0

        result = (Requests
                  .insert(name='New Request', method=1, folder=self.folder_id, collection=get_current_collection())
                  .execute())

        self.main_window_instance.query_panel.refresh(self.folder_id)

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
            # request
            req = Requests.get(Requests.id == int(selected_request()))
            folder_id = req.folder
            req.delete_instance()

            # body
            e_body = (Body.select().where(Body.request == int(selected_request()))).first()
            if e_body is not None:
                body = Body.get(Body.request == int(selected_request()))
                body.delete_instance()

            # params
            e_params = (Params.select().where(Params.request == int(selected_request()))).first()
            if e_params is not None:
                param = Params.get(Params.request == int(selected_request()))
                param.delete_instance()

            # headers
            e_headers = (Headers.select().where(Headers.request == int(selected_request()))).first()
            if e_headers is not None:
                headers = Headers.get(Headers.request == int(selected_request()))
                headers.delete_instance()

            self.refresh(node_to_expand=int(folder_id))

        elif response == Gtk.ResponseType.CANCEL:
            print("The Cancel button was clicked")

        dialog.destroy()

    def on_row_expanded(self, treeview, iter, path):
        treeiter = self.treestore.get_iter(path)
        self.treestore.set_value(treeiter, 3, "folder-open-symbolic")

    def on_row_collapsed(self, treeview, iter, path):
        treeiter = self.treestore.get_iter(path)
        self.treestore.set_value(treeiter, 3, "folder-symbolic")

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
