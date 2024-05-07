import gi

from utils.misc import get_name_by_type, get_type_color_label

gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Pango


class QueryItem(Gtk.ListBoxRow):
    def __init__(self, request):
        super().__init__()
        self.request = request
        font_desc = Pango.FontDescription("sans 12")

        self.id = request.id
        self.set_name("rbox")
        self.hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=30)  # lista
        self.hbox.set_name("hbox")

        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)  # filas
        self.hbox.set_name("vbox")

        self.item_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.hbox.set_name("ibox")

        self.vbox.set_hexpand(True)

        self.label_title = Gtk.Label()
        self.label_title.set_markup(
            "<span size=\"" + str(int(font_desc.get_size())) + "\"><b>" + request.name + "</b></span>")
        self.label_title.set_justify(Gtk.Justification.LEFT)
        self.label_title.set_margin_start(10)
        self.label_title.set_margin_top(10)
        self.label_title.set_xalign(0)

        self.label_subtitle = Gtk.Label()
        self.label_subtitle.set_markup(
            "<span weight='light' color='#dddddd' size='medium'>" + request.url + "</span>")
        self.label_subtitle.set_margin_start(10)
        self.label_subtitle.set_margin_bottom(10)
        self.label_subtitle.set_xalign(0)
        self.label_subtitle.set_justify(Gtk.Justification.LEFT)

        self.label_type = Gtk.Label()
        self.label_type.set_markup(
            "<span color='#ffffff' size='medium'>   " + get_name_by_type(request.type) + "   </span>")
        self.label_type.set_name(get_type_color_label(request.type))
        self.label_type.set_xalign(2)
        self.label_type.set_margin_end(10)
        self.label_type.set_margin_top(17)
        self.label_type.set_margin_bottom(17)
        self.label_type.set_hexpand(False)
        self.label_type.set_vexpand(False)

        self.item_box.append(self.label_title)
        self.item_box.append(self.label_subtitle)

        self.vbox.append(self.item_box)
        self.hbox.append(self.vbox)
        self.item_box.set_halign(Gtk.Align.START)

        self.hbox.append(self.label_type)

        self.set_child(self.hbox)
