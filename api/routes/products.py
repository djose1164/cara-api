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
    fetched = Product.get_product(identifier)
    if fetched is None:
        return response_with(resp.SERVER_ERROR_404)
    fetched = ProductSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"product": fetched})


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

@product_routes.route("/<identifier>", methods=["PATCH"])
def modify_product(identifier):
    get_product = Product.get_product(identifier)
    if get_product is None:
        return response_with(resp.SERVER_ERROR_404)
    
    data = request.get_json()
    if data.get("name"):
        get_product.name = data["name"]
    if data.get("sell_price"):
        get_product.sell_price = data["sell_price"]
    if data.get("buy_price"):
        get_product.buy_price = data["buy_price"]
    
    db.session.add(get_product)
    db.session.commit()
    
    product = ProductSchema.dump(get_product)
    return response_with(resp.SUCCESS_200, value={"product": product})

@product_routes.route("/<identifier>", methods=["DELETE"])
def delete_product(identifier):
    if identifier.isdecimal():
        fetched = Product.query.filter_by(id=identifier).first_or_404()
    else:
        fetched = Product.query.filter_by(name=identifier).first_or_404()
    db.session.delete(fetched)
    db.session.commit()
    return response_with(resp.SUCCESS_204)
