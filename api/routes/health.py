import os
from flask import Blueprint
from packaging.version import Version

import api.utils.responses as resp
from api.utils.responses import response_with


health_routes = Blueprint("health_routes", __name__)



@health_routes.route("/<version_code>")
def status(version_code: str):
    maintenance_on = os.environ.get("MAINTENANCE_MODE")
    maintenance_img_url = os.environ.get("MAINTENANCE_IMAGE_URL")
    maintenance_msg = os.environ.get("MAINTENANCE_MESSAGE")
    lowest_supported_version = os.environ.get("CLIENT_LOWEST_SUPPORTED_VERSION")
    
    if maintenance_on == "True":
        return response_with(
            resp.SERVER_ERROR_503,
            message=f'<img src="{maintenance_img_url}" height="200" width="200"><p>{maintenance_msg}</p>',
        )
    if Version(version_code) >= Version(lowest_supported_version):
        return response_with(resp.SUCCESS_200, value={"status": "OK"})
    else:
        return response_with(
            resp.UPGRADE_REQUIRED,
            message=f"The lowest supported client version is {lowest_supported_version}.",
        )
