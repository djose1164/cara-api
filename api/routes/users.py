from flask import Blueprint, request

from api.models.users import User, UserSchema
import api.utils.responses as resp
from api.utils.responses import response_with

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if data.get("email") is None:
            return response_with(resp.INVALID_INPUT_422)
        if User.find_by_email(data["email"]):
            return response_with(resp.CREDENTIALS_NOT_AVAILABLE_422)
        data["password"] = User.generate_hash(data["password"])
        user = UserSchema().load(data)
        user.create()
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@user_routes.route("/login", methods=["POST"])
def authenticate_user():
    try:
        data = request.get_json()
        current_user = None
        print(data)
        if "@" not in data["username"]:
            current_user = User.find_by_username(data["username"])
        else:
            current_user = User.find_by_email(data["username"])

        if current_user is None:
            return response_with(resp.SERVER_ERROR_404)
        if User.verify_hash(data["password"], current_user.password):
            return response_with(
                resp.SUCCESS_201, value={"message": "You're logged in!"}
            )
        else:
            return response_with(resp.CREDENTIALS_NOT_VALID_422)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@user_routes.route("/<user>", methods=["GET"])
def user_info(user):
    if "@" in user:
        current_user = User.query.filter_by(email=user).first_or_404()
    else:
        current_user = User.query.filter_by(username=user).first_or_404()
    fetched = UserSchema().dump(current_user)
    return response_with(resp.SUCCESS_200, {"user": fetched})
