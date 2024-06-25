import gi
from gi.repository import Gtk

gi.require_version('Gtk', '3.0')


class EnvironmentWindow(Gtk.Dialog):
    def __init__(self, main_window_instance=None, modify=False):
        super().__init__(title="Environments")

        self.main_window_instance = main_window_instance
        self.set_default_size(800, 600)
        self.set_modal(True)
        self.set_resizable(False)

