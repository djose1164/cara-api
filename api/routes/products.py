from flask import Blueprint, request

import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db
from api.models.products import Product, ProductSchema

product_routes = Blueprint("products_route", __name__)


@product_routes.route("/")
def product_index():
    fetched = Product.query.all()
    fetched = ProductSchema().dump(fetched, many=True)
    return response_with(resp.SUCCESS_200, value={"products": fetched})


@product_routes.route("/<identifier>")
def get_product(identifier):
    fetched = None
    if identifier.isdecimal():
        fetched = Product.query.filter_by(id=identifier).first_or_404()
    else:
        identifier.capitalize()
        fetched = Product.query.filter_by(name=identifier).first_or_404()

    if fetched:
        fetched = ProductSchema().dump(fetched)
        return response_with(resp.SUCCESS_200, value={"product": fetched})
    else:
        return response_with(resp.SERVER_ERROR_404)


@product_routes.route("/", methods=["POST"])
def add_product():
    try:
        data = request.get_json()
        product = ProductSchema().load(data)
        product.create()
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)


@product_routes.route("/<identifier>", methods=["DELETE"])
def delete_product(identifier):
    if identifier.isdecimal():
        fetched = Product.query.filter_by(id=identifier).first_or_404()
    else:
        fetched = Product.query.filter_by(name=identifier).first_or_404()
    db.session.delete(fetched)
    db.session.commit()
    return response_with(resp.SUCCESS_204)
