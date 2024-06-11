# import gi
#
# gi.require_version('Gtk', '3.0')
# from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib
#
#
# def do_measure(orientation, for_size):
#     print("m")
#     return 50, 50, -1, -1
#     pass
#
#
# class Custom(Gtk.Widget):
#     def __init__(self):
#         super().__init__()
#         self.set_size_request(30, 30)
#
#     def do_snapshot(self, s):
#         #s.save()
#         print("sn")
#         red = Gdk.RGBA()
#         # red.red = 1.
#         # red.green = 0.
#         # red.blue = 0.
#         # red.alpha = 1.
#         r = Graphene.Rect()
#         r.init(0, 0, 70, 70)
#         print(r)
#         print(r.get_height())
#         red.red = 1
#         red.alpha = 1
#         print(red.to_string())
#         s.append_color(red, r)
#         #s.restore()
#
