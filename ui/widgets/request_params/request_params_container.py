import gi

from ui.widgets.request_params.param_item import ParamItem

gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '4')

from gi.repository import Gtk


class RequestParamsContainer(Gtk.Box):
    def __init__(self, parent=None):
        self.parent = None
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.params_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        self.label_params_description = Gtk.Label()
        self.label_params_description.set_xalign(0)
        self.label_params_description.set_hexpand(True)
        self.label_params_description.set_margin_top(0)
        self.label_params_description.set_margin_start(10)
        self.label_params_description.set_markup("<span weight='light' size='large'>Query Params</span>")
        self.params_container.add(self.label_params_description)

        self.list_box_params = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.list_box_params.set_margin_top(0)
        self.list_box_params.set_hexpand(True)

        self.box = Gtk.Box()
        self.icon = Gtk.Image(icon_name="list-add-symbolic")
        self.box.add(self.icon)
        self.box.set_tooltip_text('Add Param')
        self.button = Gtk.Button(child=self.box)
        self.button.set_name("add-button")
        self.button.set_margin_top(10)
        self.button.set_margin_end(10)
        self.button.connect("clicked", lambda button: self.list_box_params.add(ParamItem(parent)))
        self.params_container.add(self.button)

        self.list_box_params.add(self.params_container)
        self.add(self.list_box_params)
        self.show_all()