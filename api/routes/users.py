import os
from flask import Blueprint, request
print(os.getcwd())
from api.models.users import User, UserSchema
import api.utils.responses as resp
from api.utils.responses import response_with

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        conditions = [
            User.find_by_username(data["username"]) or User.find_by_email(data["email"])
        ]
        if all(conditions):
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
        
        if data.get("username"):
            current_user = User.find_by_username(data["username"])
        elif data.get("email"):
            current_user = User.find_by_email(data["email"])
        
        if current_user is None:
            return response_with(resp.SERVER_ERROR_404)
        if User.verify_hash(data["password"], current_user.password):
            return response_with(resp.SUCCESS_201, value={"message": "You're logged in!"})
        else:
            return response_with(resp.CREDENTIALS_NOT_VALID_422)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)
    
