import os
from api.config.config import Config
from werkzeug.utils import secure_filename
from typing import Callable


def save_file(file, upload_folder: str = Config.UPLOAD_FOLDER):
    filename = secure_filename(file.filename)
    file.save(os.path.join(upload_folder, filename))


def save_file_list(
    files, callback: Callable = None, upload_folder: str = Config.UPLOAD_FOLDER
):
    for f in files:
        save_file(f, upload_folder)
        callback(secure_filename(f.filename))
