import json

import gi

gi.require_version('Gtk', '4.0')
gi.require_version('GtkSource', '5')

from gi.repository import Gtk, GtkSource


class SourceView(GtkSource.View):
    def __init__(self, buffer, editable=bool):
        super().__init__()

        self.set_buffer(buffer)

        # Set properties of the view
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.set_show_line_numbers(True)
        self.set_editable(editable)
        self.set_wrap_mode(Gtk.WrapMode.WORD)
        language_manager = GtkSource.LanguageManager.new()
        json_lang = language_manager.get_language("json")
        buffer.set_language(json_lang)

        style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
        style_scheme = style_scheme_manager.get_scheme('Adwaita-dark')
        if style_scheme:
            buffer.set_style_scheme(style_scheme)

        bt = Gtk.Button(label="format")
        bt.set_tooltip_text("Format Code")
        bt.set_halign(Gtk.Align.END)
        bt.connect("clicked", self.format_code)
        #self.add_overlay(child=bt, xpos=self.get_allocated_width(), ypos=self.get_allocated_width())

    def format_code(self, event):
        start_iter = self.get_buffer().get_start_iter()
        end_iter = self.get_buffer().get_end_iter()
        text = self.get_buffer().get_text(start_iter, end_iter, True)
        parsed_json = json.loads(text)
        formatted_json = json.dumps(parsed_json, indent=8)
        self.get_buffer().set_text(formatted_json)

