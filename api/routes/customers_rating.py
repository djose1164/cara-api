from flask import Blueprint, request

from api.models.customers import Customer
from api.models.customers_rating import CustomersRatingSchema, CustomersRating
from api.utils.responses import response_with
import api.utils.responses as resp
from api.utils.database import db
import datetime as dt
import pytz

rating_routes = Blueprint("rating_routes", __name__)


def SantoDomingoDatetime():
    tz = pytz.timezone("America/Santo_Domingo")
    time = dt.datetime.now(tz)
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    return current_time


@rating_routes.route("/")
def get_rating():
    args = request.args

    product_id = args.get("product_id")
    customer_id = args.get("customer_id")

    if product_id is None:
        fetched = CustomersRating.query.all()
        fetched = CustomersRatingSchema(many=True, exclude=("customer",)).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"ratings": fetched})
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
                resp.FORBIDDEN_403,
                message="Debes haber comprado el producto para poder dejar tu calificación.",
            )
        date = SantoDomingoDatetime()
        print("## date ", date)
        data.update({"posted_date": date})
        rating = CustomersRatingSchema().load(data)
        rating.create()

        return response_with(resp.SUCCESS_200, value={"rating_id": rating.id})
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@rating_routes.route("/<int:rating_id>", methods=["PATCH"])
def update_rating(rating_id):
    try:
        print("PATCHING")
        data = request.get_json()
        fetched = CustomersRating.get_rating_by_id(rating_id)
        if data.get("review") is not None:
            fetched.review = data["review"]
        if data.get("rating") is not None:
            fetched.rating = data["rating"]

        db.session.add(fetched)
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
