import gi
from gi.repository import Gtk

from src.utils.database import Environments

gi.require_version('Gtk', '3.0')


class EnvironmentWindow(Gtk.Dialog):
    def __init__(self, main_window_instance=None, modify=False):
        super().__init__(title="Environments")

        self.main_window_instance = main_window_instance
        self.set_default_size(800, 600)
        self.set_modal(True)
        self.set_resizable(False)

        self.env_notebook = Gtk.Notebook()
        self.env_notebook.set_vexpand(True)
        self.env_notebook.set_hexpand(True)
        self.env_notebook.set_tab_pos(Gtk.PositionType.LEFT)

        box = self.get_content_area()

        box.add(self.env_notebook)

        self.get_environments()

        self.show_all()

    def get_environments(self):
        results = Environments.select()
        for env in results:
            self.env_notebook.append_page(Gtk.Label(label=env.name), Gtk.Label(label=env.name))
