import gi

from src.utils.misc import get_name_by_type, get_type_color_label

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango


class QueryItem(Gtk.ListBoxRow):
    def __init__(self, request):
        super().__init__()
        self.request = request
        font_desc = Pango.FontDescription("sans 12")

        self.id = request.id
        self.set_name("rbox")
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)  # lista
        self.hbox.set_name("hbox")

        self.label_title = Gtk.Label()
        self.label_title.set_markup(
            "<span size=\"" + str(int(font_desc.get_size())) + "\"><b>" + request.name + "</b></span>")
        self.label_title.set_justify(Gtk.Justification.LEFT)
        self.label_title.set_margin_top(0)
        self.label_title.set_xalign(1)
        self.label_subtitle = Gtk.Label()
        self.label_subtitle.set_markup(
            "<span weight='light' size='medium'>" + request.url + "</span>")
        self.label_subtitle.set_margin_start(10)
        self.label_subtitle.set_margin_bottom(10)
        self.label_subtitle.set_xalign(0)
        self.label_subtitle.set_justify(Gtk.Justification.LEFT)

        self.label_type = Gtk.Label()
        self.label_type.set_markup(
            "<span color='#ffffff' size='medium'>   " + get_name_by_type(request.method) + "   </span>")
        self.label_type.set_name(get_type_color_label(request.method))
        self.label_type.set_xalign(1)
        self.label_type.set_margin_start(10)
        self.label_type.set_margin_end(5)
        self.label_type.set_margin_top(17)
        self.label_type.set_margin_bottom(17)
        self.label_type.set_hexpand(False)
        self.label_type.set_vexpand(False)

        self.hbox.add(self.label_type)
        self.hbox.add(self.label_title)

        # self.hbox.add(self.vbox)
        # self.item_box.set_halign(Gtk.Align.START)
        #
        # self.hbox.add(self.label_type)

        self.add(self.hbox)
