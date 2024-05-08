import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk


class HeaderStatus(Gtk.Box):
    def __init__(self, main_window_instance):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        self.set_margin_top(20)
        self.set_margin_bottom(15)
        self.set_margin_start(10)
        self.label_status = Gtk.Label()
        self.label_status.set_markup("<span weight='light' size='medium'>Status: </span><span weight='bold' "
                                     "color='#008800'></span>")
        self.label_size = Gtk.Label()
        self.label_size.set_markup("<span weight='light' size='medium'>Size: </span><span weight='bold' "
                                   "color='#008800'>0 Bytes</span>")
        self.label_time = Gtk.Label()
        self.label_time.set_markup("<span weight='light' size='medium'>Time: </span><span weight='bold' "
                                   "color='#008800'>0 ms</span>")

        box = Gtk.Box(spacing=6)
        icon = Gtk.Image(icon_name="system-run-symbolic")
        label = Gtk.Label(label="Run")
        box.add(icon)
        box.add(label)
        button = Gtk.Button(child=box)
        button.set_halign(Gtk.Align.END)
        button.set_margin_end(10)
        button.set_hexpand(True)  # trick to right align
        button.connect("clicked", main_window_instance.make_request)

        self.add(self.label_status)
        self.add(self.label_size)
        self.add(self.label_time)
        self.add(button)

    def update_data(self, response):
        status = response.status
        elapsed = int(response.elapsed * 1000)
        content_length = response.headers.get('Content-Length')

        # Define markup templates
        markup_status = "<span weight='light' size='medium'>Status: </span><span weight='bold' color='{}'>{}</span>"
        markup_size = "<span weight='light' size='medium'>Size: </span><span weight='bold' color='{}'>{} Bytes</span>"
        markup_time = "<span weight='light' size='medium'>Time: </span><span weight='bold' color='{}'>{} ms</span>"

        # Set color based on status range
        color = '#008800' if 200 <= status < 300 else '#ff0000'

        # Update labels
        self.label_status.set_markup(markup_status.format(color, status))
        self.label_size.set_markup(markup_size.format(color, content_length))
        self.label_time.set_markup(markup_time.format(color, elapsed))

