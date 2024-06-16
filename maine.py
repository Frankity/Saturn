import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="HeaderBar with Paned Example")
        self.set_default_size(800, 600)

        # Crear HeaderBar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "Mi Aplicación"
        self.set_titlebar(header)

        # Botón en el HeaderBar
        button = Gtk.Button(label="Botón")
        header.pack_end(button)

        # Crear Paned (Split view)
        paned = Gtk.Paned()
        self.add(paned)

        # Crear panel izquierdo
        panel_izquierdo = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        panel_izquierdo.set_border_width(10)
        panel_izquierdo.add(Gtk.Label(label="Panel Izquierdo"))
        paned.pack1(panel_izquierdo, resize=True, shrink=False)

        # Crear panel derecho
        panel_derecho = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        panel_derecho.set_border_width(10)
        panel_derecho.add(Gtk.Label(label="Panel Derecho"))
        paned.pack2(panel_derecho, resize=True, shrink=False)

        self.connect("destroy", Gtk.main_quit)

win = MyWindow()
win.show_all()
Gtk.main()
