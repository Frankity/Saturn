import json
from urllib.parse import urlparse

from src.utils.methods import items
from gi.repository import Gio


def get_type_by_name(name):
    for item in items:
        if item["name"].lower() == name.lower():
            return item["type"]
    return None


def get_name_by_type(tpe):
    for item in items:
        if item["type"] == tpe:
            return item["name"]
    return None


def get_color_by_method(tpe):
    if tpe == 1:
        return '#008800'
    elif tpe == 2:
        return '#007FFF'
    elif tpe == 3:
        return '#FFA500'
    elif tpe == 4:
        return '#FF0000'
    elif tpe == 5:
        return '#9F27B7'


def get_type_color_label(tpe):
    if tpe == 1:
        return 'type-get-label'
    elif tpe == 2:
        return 'type-post-label'
    elif tpe == 3:
        return 'type-post-label'
    elif tpe == 4:
        return 'type-delete-label'


def selected_request():
    from src.ui.main_window import app_settings
    return app_settings.get_int('selected-row')


def set_current_collection(collection_id):
    app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')
    app_settings.set_int('selected-collection', collection_id)


def get_current_collection():
    from src.ui.main_window import app_settings
    return app_settings.get_int('selected-collection')


def set_current_folder(folder_id):
    app_settings = Gio.Settings.new(schema_id='xyz.frankity.saturn')
    app_settings.set_int('selected-folder', folder_id)


def get_current_folder():
    from src.ui.main_window import app_settings
    try:
        s_folder = app_settings.get_int('selected-folder')
        return s_folder
    except Exception as e:
        return 0

class SingleQuoteEncoder(json.JSONEncoder):
    def encode_string(self, s):
        # Replace double quotes with single quotes
        return "'" + s.replace("'", "\\'") + "'"


def get_domain_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain
