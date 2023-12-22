from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import text
from api.models.statistics import CustomerStatisticsSchema, ProductStatisticsSchema
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp

statistics_routes = Blueprint("statistics_routes", __name__)


@statistics_routes.route("/")
@jwt_required()
def index():
    products = db.session.execute(text("SELECT * FROM product_statistics;"))
    bill_statistics = db.session.execute(text("SELECT * FROM bill_statistics"))

    products = ProductStatisticsSchema(many=True).dump(products)
    customers = CustomerStatisticsSchema(many=True).dump(bill_statistics)
    return response_with(
        resp.SUCCESS_200,
        value={
            "statistics": {
                "most_selling_products": products,
                "customers": customers,
            }
        },
    )


@statistics_routes.route("/<int:salesperson_id>/products")
@jwt_required()
def product_statistics(salesperson_id):
    products = db.session.execute(
        text("CALL salesperson_product_statistics(:salesperson_id)"), {"salesperson_id": salesperson_id}
    )
    products = ProductStatisticsSchema(many=True).dump(products)
    return response_with(resp.SUCCESS_200, value={"most_selling_products": products})

@statistics_routes.route("/<int:salesperson_id>/customers")
@jwt_required()
def customers_statistics(salesperson_id):
    customers = db.session.execute(
        text("CALL salesperson_customer_statistics(:salesperson_id)"), {"salesperson_id": salesperson_id}
    )
    customers = CustomerStatisticsSchema(many=True).dump(customers)
    return response_with(resp.SUCCESS_200, value={"customers_statistics": customers})
