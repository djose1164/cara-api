from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from api.models.customers import Customer
from api.models.users import User, UserSchema
from api.models.favorite_products import FavoriteProduct, FavoriteProductSchema

import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

user_routes = Blueprint("user_routes", __name__)


@user_routes.route("/", methods=["POST"])
def create_user():
    try:
        data = request.get_json()

        if data.get("username"):
            return create_user_for_customer(data)
        elif data.get("contact") and data["contact"].get("email"):
            return create_user_for_salesperson(data)
        else:
            return response_with(resp.CREDENTIALS_NOT_AVAILABLE_422)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


def create_user_for_salesperson(data: dict):
    try:
        if User.find_by_email(data["contact"]["email"]):
            return response_with(resp.CREDENTIALS_NOT_AVAILABLE_422)

        user = UserSchema().load(data, partial=True)
        user.generate_username(data["forename"] + data["surname"])

        db.session.add(user)
        db.session.commit()
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


def create_user_for_customer(data: dict):
    user_schema = UserSchema()
    user: User = user_schema.load(data, partial=True)
    db.session.add(user)
    db.session.flush()

    customer = Customer(contact_id=user.contact_id, user_id=user.id)
    db.session.add(customer)
    db.session.commit()
    return response_with(resp.SUCCESS_200, value={"user": user_schema.dump(user)})


@user_routes.route("/<int:identifier>")
@jwt_required()
def get_user(identifier: int):
    fetched = User.find_by_id(identifier)
    fetched = UserSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, {"user": fetched})


@user_routes.route("/<int:identifier>")
@jwt_required()
def delete_user(identifier: int):
    fetched = User.delete_by_id(identifier)
    return response_with(resp.SUCCESS_204)


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
    
@user_routes.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        import pprint
        pprint.pprint(data)
        user_schema = UserSchema()
        new_user = user_schema.load(data)
        db.session.add(new_user)
        db.session.flush()
        new_user.customer = Customer(person_id=new_user.person_id, user_id=new_user.id)
        new_user.create()
        return response_with(resp.SUCCESS_201, value={"user": user_schema.dump(new_user)})
    except Exception as e:
        db.session.rollback()
        print(e)
        return response_with(resp.SERVER_ERROR_500)


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


@user_routes.route("/<int:user_id>/favorites", methods=["POST"])
@jwt_required()
def add_favorite(user_id: int):
    try:
        product_id = request.json.get("product_id")

        favorite = db.session.execute(
            db.select(FavoriteProduct)
            .filter_by(user_id=user_id)
            .filter_by(product_id=product_id)
        ).scalar()
        if favorite is not None:
            return response_with(
                resp.SERVER_ERROR_500, message="The favorite already exists."
            )

        if product_id is None:
            return response_with(
                resp.INVALID_INPUT_422, message="product_id is missing."
            )

        favorite = FavoriteProduct(product_id=product_id, user_id=user_id)
        favorite.create()
        return response_with(
            resp.SUCCESS_201, value={"favorite": FavoriteProductSchema().dump(favorite)}
        )
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422, message=e)


@user_routes.route("/<int:user_id>/favorites")
@jwt_required()
def read_favorites_by_user_id(user_id: int):
    try:
        favorites = db.session.execute(
            db.select(FavoriteProduct).filter_by(user_id=user_id)
        ).scalars()
        print(favorites)
        return response_with(
            resp.SUCCESS_200,
            value={"favorites": FavoriteProductSchema(many=True).dumps(favorites)},
        )
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@user_routes.route("/<int:user_id>/favorites/<int:favorite_id>", methods=["DELETE"])
@jwt_required()
def delete_favorite(user_id, favorite_id: int):
    try:
        favorite = db.get_or_404(FavoriteProduct, favorite_id)
        db.session.delete(favorite)
        db.session.commit()
        return response_with(resp.SUCCESS_204)
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400, message=str(e))


@user_routes.route("/<int:user_id>", methods=["PATCH"])
def patch_user(user_id: int):
    user: User = db.get_or_404(User, user_id)
    data = request.json
    if data.get("password"):
        if not data["password"].get("new_password") and not data["password"].get(
            "current_password"
        ):
            return response_with(
                resp.INVALID_INPUT_422,
                message="current_password or new_password is missing.",
            )
        if not User.verify_hash(data["password"]["current_password"], user.password):
            return response_with(
                resp.UNAUTHORIZED_401, message="La contraseña actual es incorrecta."
            )
        user.password = User.generate_hash(data["password"]["new_password"])

    db.session.add(user)
    db.session.commit()
    return response_with(resp.SUCCESS_200)
