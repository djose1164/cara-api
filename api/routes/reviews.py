from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from api.models.customers import Customer
from api.models.reviews import ReviewSchema, Review
from api.utils.responses import response_with
import api.utils.responses as resp
from api.utils.database import SantoDomingoDatetime, db


rating_routes = Blueprint("rating_routes", __name__)


@rating_routes.route("/")
def get_rating():
    args = request.args

    product_id = args.get("product_id")
    customer_id = args.get("customer_id")

    if product_id is None and customer_id is None:
        fetched = Review.query.all()
        fetched = ReviewSchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"reviews": fetched})
    if customer_id is None and product_id:
        fetched = get_rating_by_product_id(product_id)
        return response_with(resp.SUCCESS_200, value={"reviews": fetched})
    if customer_id and product_id is None:
        fetched = db.session.execute(
            db.select(Review).filter_by(customer_id=customer_id)
        ).scalars()
        fetched = ReviewSchema(many=True).dump(fetched)
        return response_with(resp.SUCCESS_200, value={"reviews": fetched})

    customer_rating = Review.find_rating(customer_id, product_id)
    if customer_rating is None:
        print("Not found")
        return response_with(resp.SERVER_ERROR_404)
    else:
        fetched = ReviewSchema().dump(customer_rating)
        return response_with(resp.SUCCESS_200, value={"review": fetched})


@rating_routes.route("/<int:rating_id>")
def get_rating_by_id(rating_id):
    fetched = Review.get_rating_by_id(rating_id)
    fetched = ReviewSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"review": fetched})


def get_rating_by_product_id(product_id):
    fetched = Review.find_product_rating(product_id)
    return ReviewSchema(exclude=("product_id",), many=True).dump(fetched)


@rating_routes.route("/can_review", methods=["GET"])
def can_customer_make_review():
    customer_id = int(request.args.get("customer_id"))
    product_id = int(request.args.get("product_id"))
    customer = db.get_or_404(Customer, customer_id)
    can_rate = any(
        detail.product_id == product_id
        for order in customer.orders
        for detail in order.order_details
    )
    return response_with(resp.SUCCESS_200 if can_rate else resp.FORBIDDEN_403)


@rating_routes.route("/", methods=["POST"])
@jwt_required()
def create_rating():
    try:
        data = request.get_json()
        if data.get("customer_id") is None:
            return response_with(
                resp.MISSING_PARAMETERS_422, message="El id del cliente es necesario."
            )
        if data.get("product_id") is None:
            return response_with(
                resp.MISSING_PARAMETERS_422, message="El id del producto es necesario."
            )
        if data.get("rating") and int(data["rating"]) < 1:
            return response_with(resp.INVALID_INPUT_422, message="Invalid star rating.")
            

        review_schema = ReviewSchema()
        rating = review_schema.load(data)
        rating.create()

        return response_with(
            resp.SUCCESS_200, value={"review": review_schema.dump(rating)}
        )
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@rating_routes.route("/<int:rating_id>", methods=["PATCH"])
@jwt_required()
def update_rating(rating_id):
    try:
        data = request.get_json()
        fetched = Review.get_rating_by_id(rating_id)
        if data.get("review_text") is not None:
            fetched.review_text = data["review_text"]
        if data.get("rating") is not None:
            fetched.rating = int(data["rating"])

        db.session.add(fetched)
        db.session.commit()
        return response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)


@rating_routes.route("/<int:rating_id>", methods=["DELETE"])
@jwt_required()
def delete_rating(rating_id):
    fetched = Review.get_rating_by_id(rating_id)
    fetched.delete()
    return response_with(resp.SUCCESS_204)
