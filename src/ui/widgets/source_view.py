import json
import traceback

import gi
from src.core.saturn_environments_events import SaturnEvents
from src.ui.dialogs.message_dialog import MessageDialog

from src.utils.database import Requests, Response
from src.utils.misc import selected_request

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, GtkSource, Gio, GLib


class SourceView(GtkSource.View):
    def __init__(self, buffer, editable=bool, for_events=False, pr=None):
        super().__init__()

        self.pr = pr
        self.set_buffer(buffer)

        self.context_menu_model = Gio.Menu.new()

        self.format_menu_item = Gio.MenuItem()
        self.format_menu_item.set_label("Format")
        # add this format menu actions
        self.context_menu_model.append_item(self.format_menu_item)

        # self.set_extra_menu(self.context_menu_model)

        self.action_group = Gio.SimpleActionGroup.new()

        # Connect actions
        self.action_group.connect("notify", self.on_action_activate)

        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_show_line_numbers(True)
        self.set_editable(editable)
        self.set_wrap_mode(Gtk.WrapMode.WORD)

        language_manager = GtkSource.LanguageManager.new()
        json_lang = language_manager.get_language("json")
        buffer.set_language(json_lang)

        style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
        # print(GtkSource.StyleSchemeManager.get_scheme_ids())
        style_scheme = style_scheme_manager.get_scheme('saturn')
        if style_scheme:
            buffer.set_style_scheme(style_scheme)

        bt = Gtk.Button(label="format")
        bt.set_tooltip_text("Format Code")
        bt.set_halign(Gtk.Align.END)
        bt.connect("clicked", self.format_code)
        # self.add_overlay(child=bt, xpos=self.get_allocated_width(), ypos=self.get_allocated_width())

    def on_action_activate(self, action, parameter):
        # Handle action activation here
        action_name = action.get_name()
        print(f"Action '{action_name}' activated")

    def on_button_press_event(self, widget, event):
        if event.button == 3:  # Right mouse button
            # Create a PopoverMenu with the context_menu_model
            menu = Gtk.PopoverMenu.new_from_model(self.context_menu_model)
            menu.show_all()
            menu.popup_at_pointer(None)
            return True
        return False

    def format_code(self, event):
        start_iter = self.get_buffer().get_start_iter()
        end_iter = self.get_buffer().get_end_iter()
        text = self.get_buffer().get_text(start_iter, end_iter, True)
        parsed_json = json.loads(text)
        formatted_json = json.dumps(parsed_json, indent=8)
        self.get_buffer().set_text(formatted_json)

    def run_events(self):


        global json_data
        global msg

        current_request = selected_request()

        event_text = self.get_buffer().get_text(
            self.get_buffer().get_start_iter(),
            self.get_buffer().get_end_iter(),
            True
        )

        req = Response.select().where(Response.request == current_request).first()

        try:
            json_data = json.loads(req.body)
        except json.JSONDecodeError as e:
            self.show_message_dialog(e.args)
        try:
            saturn = SaturnEvents()
            local_vars = {"responseData": json_data, "SaturnEvents": saturn}
            exec(event_text, {}, local_vars)
        except Exception as e:
            error_traceback = traceback.format_exc()
            print(error_traceback)
            if len(e.args) > 1:
                a, b = e.args
                out = f"{a} {b}"
                self.show_message_dialog(out)
            else:
                out = f"{e.args}"
                self.show_message_dialog(out)

    def show_message_dialog(self, message=None):

        dialog = MessageDialog(p=self.pr, message=message)
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            dialog.close()
