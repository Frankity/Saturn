import json

from utils.methods import items


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
        return '#007FFF'
    elif tpe == 2:
        return '#008800'
    elif tpe == 3:
        return '#FFA500'
    elif tpe == 4:
        return '#FF0000'


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
    from ui.main_window import app_settings
    return app_settings.get_int('selected-row')


class SingleQuoteEncoder(json.JSONEncoder):
    def encode_string(self, s):
        # Replace double quotes with single quotes
        return "'" + s.replace("'", "\\'") + "'"


