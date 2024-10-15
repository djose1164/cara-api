from flask import jsonify, make_response


UNAUTHORIZED_401 = {
    "http_code": 401,
    "code": "credentialsNotValid",
    "message": "Access token is not valid.",
}

CREDENTIALS_NOT_AVAILABLE_422 = {
    "http_code": 422,
    "code": "credentialsNotAvailable",
    "message": "Credentials not available.",
}

INVALID_INPUT_422 = {
    "http_code": 422,
    "code": "invalidInput",
    "message": "Invalid input",
}

MISSING_PARAMETERS_422 = {
    "http_code": 422,
    "code": "missingParameter",
    "message": "Missing parameters.",
}

BAD_REQUEST_400 = {"http_code": 400, "code": "badRequest", "message": "Bad request"}

SERVER_ERROR_500 = {"http_code": 500, "code": "serverError", "message": "Server error"}


SERVER_ERROR_503 = {
    "http_code": 503,
    "code": "ServiceUnavailable",
    "message": "The server is unavailable right now",
}


UPGRADE_REQUIRED = {
    "http_code": 426,
    "code": "upgradeRequired",
    "message": "The client version is not longer supported.",
}

SERVER_ERROR_404 = {
    "http_code": 404,
    "code": "notFound",
    "message": "Resource not found",
}

FORBIDDEN_403 = {
    "http_code": 403,
    "code": "notAuthorized",
    "message": "You are not authorized to execute this.",
}

SUCCESS_200 = {"http_code": 200, "code": "success"}
SUCCESS_201 = {"http_code": 201, "code": "success"}
SUCCESS_204 = {"http_code": 204, "code": "success"}


def response_with(
    response, value=None, message=None, error=None, headers={}, pagination=None
):
    result = {}
    if value:
        result.update(value)
    if message:
        result.update({"message": message})
    elif response.get("message"):
        result.update({"message": response["message"]})
    if error:
        result.update({"error": error})
    if pagination:
        result.update({"pagination": pagination})

    result.update({"code": response["code"]})
    headers.update({"Access-Control-Allow-Origin": "*"})
    headers.update({"server": "Cara REST API"})
    return make_response(jsonify(result), response["http_code"], headers)


def pagination_to_dict(pagination):
    return {
        "pages": pagination.pages,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }
