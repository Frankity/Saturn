import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk, Gio, Gdk


class YesNoDialog(Gtk.Dialog):
    def __init__(self, parent, title=None, message=None):
        super().__init__(title="YesNoDialog", transient_for=parent, flags=0)
        self.set_border_width(10)

        self.set_title(title)

        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(150, 100)

        label = Gtk.Label(label=f'{message}\nby clicking in OK, everything related to this request will be deleted.')
        label.set_halign(Gtk.Align.CENTER)
        box = self.get_content_area()
        box.add(label)
        self.show_all()
