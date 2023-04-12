from flask import Blueprint, request

from api.models.customers import Customer
from api.models.customers_rating import CustomersRatingSchema, CustomersRating
from api.models.products import Product
from api.utils.responses import response_with
import api.utils.responses as resp
from api.utils.database import db

rating_routes = Blueprint("rating_routes", __name__)


@rating_routes.route("/")
def get_rating():
    args = request.args

    product_id = args.get("product_id")
    customer_id = args.get("customer_id")

    if product_id is None:
        return response_with(resp.BAD_REQUEST_400)
    if customer_id is None:
        fetched = get_rating_by_product_id(product_id)
        return response_with(resp.SUCCESS_200, value={"ratings": fetched})

    customer_rating = CustomersRating.find_rating(customer_id, product_id)
    if customer_rating is None:
        print("Not found")
        return response_with(resp.SERVER_ERROR_404)
    else:
        fetched = CustomersRatingSchema().dump(customer_rating)
        return response_with(resp.SUCCESS_200, value={"rating": fetched})


@rating_routes.route("/<int:rating_id>")
def get_rating_by_id(rating_id):
    fetched = CustomersRating.get_rating_by_id(rating_id)
    fetched = CustomersRatingSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"rating": fetched})


def get_rating_by_product_id(product_id):
    fetched = CustomersRating.find_product_rating(product_id)
    return CustomersRatingSchema(
        only=("name", "review", "rating", "posted_date", "customer_id", "id"), many=True
    ).dump(fetched)


@rating_routes.route("/", methods=["POST"])
def create_rating():
    try:
        data = request.get_json()
        if data.get("customer_id") is None:
            return response_with(
                resp.MISSING_PARAMETERS_422, message="El id del cliente es necesario."
            )

        customer = Customer.find_by_id(data["customer_id"])
        can_rate = False
        for order in customer.orders:
            for detail in order.order_details:
                if detail.product_id == data["product_id"]:
                    can_rate = True
                    break
        if not can_rate:
            return response_with(
                resp.UNAUTHORIZED_401,
                message="Debes haber comprado el producto para poder dejar tu calificacion.",
            )

        rating = CustomersRatingSchema().load(data)
        db.session.add(rating)
        db.session.flush()

        ratings = CustomersRating.query.all()

        customers_rating = len(ratings)
        rating_mean = sum(r.rating for r in ratings) // customers_rating

        product = Product.find_product_by_id(data["product_id"])
        product.rating = rating_mean
        product.create()

        return response_with(
            resp.SUCCESS_200, value={"rating": rating_mean, "rating_id": rating.id}
        )
    except Exception as e:
        db.session.rollback()
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@rating_routes.route("/", methods=["POST"])
def update_rating():
    try:
        data = request.get_json()
        if data.get("customer_id") is None:
            return response_with(
                resp.MISSING_PARAMETERS_422, message="El id del cliente es necesario."
            )
        if data.get("product_id") is None:
            return response_with(
                resp.MISSING_PARAMETERS_422, message="El id del product es necesario."
            )
        rating = CustomersRating.find_rating(data["customer_id"], data["product_id"])

        if rating is not None:
            rating.rating = data["rating"]
            if data.get("review") is not None:
                rating.review = data["review"]
        else:
            return response_with(resp.SERVER_ERROR_404)

        rating = CustomersRatingSchema().load(data)
        db.session.add(rating)
        db.session.commit()
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@rating_routes.route("/<int:rating_id>", methods=["DELETE"])
def delete_rating(rating_id):
    fetched = CustomersRating.get_rating_by_id(rating_id)
    fetched.delete()
    return response_with(resp.SUCCESS_204)
