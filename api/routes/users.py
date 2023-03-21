from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from api.models.person_info import PersonInfoSchema

from api.models.users import User, UserSchema
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/", methods=["POST"])
def create_user():
    try:
        data = request.get_json()
        if (
            data.get("email") is None
            or data.get("forename") is None
            or data.get("surname") is None
            or data.get("password") is None
        ):
            return response_with(resp.INVALID_INPUT_422)
        
        if User.find_by_email(data["email"]):
            return response_with(resp.CREDENTIALS_NOT_AVAILABLE_422)
        
        info = {"forename": data.pop("forename"), "surname": data.pop("surname")}
        data["password"] = User.generate_hash(data["password"])
        
        user = UserSchema().load(data)
        user.generate_username(info["forename"]+info["surname"])
        db.session.add(user)
        db.session.flush()
        try:
            info["user_id"] = user.id
            person_info = PersonInfoSchema().load(info)
            db.session.add(person_info)
            db.session.flush()
        except Exception as e:
            print(e)
            return response_with(resp.INVALID_INPUT_422) 
        else:
            db.session.commit()
            return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@user_routes.route("/login/", methods=["POST"], strict_slashes=False)
def authenticate_user():
    try:
        data = request.get_json()
        current_user = User.find_by_username(data["username"])

        if current_user is None:
            return response_with(resp.SERVER_ERROR_404)
        if User.verify_hash(data["password"], current_user.password):
            access_token = create_access_token(identity=data["username"])
            refresh_token = create_refresh_token(identity=data["username"])
            
            return response_with(
                resp.SUCCESS_200,
                value={
                    "user": UserSchema().dump(current_user),
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                message="You're logged in!",
            )
        else:
            return response_with(resp.UNAUTHORIZED_401)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)

@user_routes.route("/refresh/")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return response_with(resp.SUCCESS_200, value={"access_token": access_token})


@user_routes.route("/", methods=["GET"])
@jwt_required()
def user_info():
    identity = get_jwt_identity()
    current_user = User.query.filter_by(username=identity).first_or_404()
    fetched = UserSchema().dump(current_user)
    return response_with(resp.SUCCESS_200, {"user": fetched})
