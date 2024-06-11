import os
from src.utils.config import CONFIG_DIR, APP_DIR


def get_user_dir():
    return os.path.expanduser('~')


def create_data_directory():
    app_dir = f'{get_user_dir()}/{CONFIG_DIR}{APP_DIR}'
    try:
        if not os.path.exists(app_dir):
            os.mkdir(app_dir)
    except Exception as e:
        print(e)
