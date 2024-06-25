import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class MessageDialog(Gtk.Dialog):
    def __init__(self, p=None, message=None):
        super().__init__(title="YesNoDialog", transient_for=p, flags=0)
        self.set_border_width(10)
        self.message = message

        self.add_buttons(
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )

        self.set_default_size(150, 100)

        label = Gtk.Label(label=f'{message}')
        label.set_halign(Gtk.Align.CENTER)
        box = self.get_content_area()
        box.add(label)
        self.show_all()

    def on_button_clicked(self, widget):

        self.close()
