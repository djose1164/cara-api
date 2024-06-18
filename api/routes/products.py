import json
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from api.utils.files import save_file, save_file_list
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db
from api.models.products import Product, ProductImage, ProductImageSchema, ProductSchema

product_routes = Blueprint("products_route", __name__)


@product_routes.route("/")
def product_index():
    fetched = Product.query.order_by(Product.category_id).all()
    fetched = ProductSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"products": fetched})


@product_routes.route("/<identifier>")
def get_product_by_identifier(identifier):
    if identifier.isdecimal():
        fetched = Product.find_product_by_id(identifier)
        value = {"product": ProductSchema().dump(fetched)}
    else:
        fetched = Product.find_product_by_name(identifier)
        value = {"products": ProductSchema(many=True).dump(fetched)}

    if fetched is None:
        return response_with(resp.SERVER_ERROR_404)
    return response_with(resp.SUCCESS_200, value=value)


@product_routes.route("/", methods=["POST"])
@jwt_required()
def add_product():
    try:
        product_json = json.loads(request.form["jsonData"])
        product_schema = ProductSchema()
        new_product: Product = product_schema.load(product_json)
        db.session.add(new_product)
        db.session.flush()

        images = request.files.getlist("image")
        print("images: ",images)
        for img in images:
            save_file(img)
            product_image = ProductImage(
                image_url=img.filename, product_id=new_product.id
            )
            db.session.add(product_image)
            new_product.images.append(product_image)

        new_product.create()
        return response_with(
            resp.SUCCESS_200, value={"product": ProductSchema().dump(new_product)}
        )
    except Exception as e:
        print(e)
        db.session.rollback()
        return response_with(resp.INVALID_INPUT_422)


@product_routes.route("/<identifier>", methods=["PATCH"])
@jwt_required()
def modify_product(identifier):
    get_product: Product = Product.find_product_by_id(identifier)
    if get_product is None:
        return response_with(resp.SERVER_ERROR_404)

    data = request.get_json()
    if data.get("name"):
        get_product.name = data["name"]
    if data.get("sell_price"):
        get_product.sell_price = data["sell_price"]
    if data.get("buy_price"):
        get_product.buy_price = data["buy_price"]
    if data.get("description"):
        get_product.description = data["description"]
    if data.get("category_id"):
        get_product.category_id = data["category_id"]
    db.session.add(get_product)
    db.session.commit()

    product = ProductSchema().dump(get_product)
    return response_with(resp.SUCCESS_200, value={"product": product})


@product_routes.route("/<int:identifier>", methods=["PUT"])
@jwt_required()
def update_product(identifier: int):
    try:
        data = request.get_json()
        get_product = Product.find_product_by_id(identifier)

        product = ProductSchema().load(data, instance=get_product)
        product.create()
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@product_routes.route("/<identifier>", methods=["DELETE"])
@jwt_required()
def delete_product(identifier):
    if identifier.isdecimal():
        fetched = Product.query.filter_by(id=identifier).first_or_404()
    else:
        fetched = Product.query.filter_by(name=identifier).first_or_404()
    db.session.delete(fetched)
    db.session.commit()
    return response_with(resp.SUCCESS_204)


@product_routes.route("/<int:identifier>/picture", methods=["POST"])
@jwt_required()
def add_product_picture(identifier):
    fetched: Product = Product.query.filter_by(id=identifier).first_or_404()
    save_file_list(
        request.files.getlist("image"),
        lambda filename: fetched.images.append(
            ProductImage(image_url=filename, product_id=fetched.id)
        ),
    )
    db.session.add(fetched)
    db.session.commit()

    images = db.session.execute(
        db.select(ProductImage).filter_by(product_id=identifier)
    ).scalars()
    return response_with(
        resp.SUCCESS_201, value={"images": ProductImageSchema(many=True).dump(images)}
    )


@product_routes.route("/picture/<int:identifier>", methods=["DELETE"])
@jwt_required()
def delete_product_picture(identifier):
    fetched = ProductImage.query.filter_by(id=identifier).first_or_404()
    db.session.delete(fetched)
    db.session.commit()
    return response_with(resp.SUCCESS_204)


@product_routes.route("/<int:identifier>/picture")
def product_picture(identifier):
    images = db.session.execute(
        db.select(ProductImage).filter_by(product_id=identifier)
    ).scalars()
    return response_with(
        resp.SUCCESS_200, value={"images": ProductImageSchema(many=True).dump(images)}
    )
