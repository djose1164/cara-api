import os
from flask import Blueprint
from packaging.version import Version

import api.utils.responses as resp
from api.utils.responses import response_with


health_routes = Blueprint("health_routes", __name__)



@health_routes.route("/<version_code>")
def status(version_code: str):
    maintenance_on = os.environ.get("MAINTENANCE_MODE")
    lowest_supported_version = os.environ.get("CLIENT_LOWEST_SUPPORTED_VERSION")
    if maintenance_on == "True":
        return response_with(
            resp.SERVER_ERROR_503,
            message='<img src="https://cdn.dribbble.com/users/1801739/screenshots/15012625/media/e64203da9fdc4df221bfc8d79ab6ef0f.png?resize=360x0"><p>Estamos trabajando...</p>',
        )
    if Version(version_code) >= Version(lowest_supported_version):
        return response_with(resp.SUCCESS_200, value={"status": "OK"})
    else:
        return response_with(
            resp.UPGRADE_REQUIRED,
            message=f"The lowest supported client version is {lowest_supported_version}.",
        )
