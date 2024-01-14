from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from sqlalchemy import text
from api.models.statistics import (
    CustomerStatisticsSchema,
    MonthVsOrderQtySchema,
    PaymentStatusStatisticsSchema,
    ProductStatisticsSchema,
)
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
        text("CALL salesperson_product_statistics(:salesperson_id)"),
        {"salesperson_id": salesperson_id},
    )
    products = ProductStatisticsSchema(many=True).dump(products)
    return response_with(resp.SUCCESS_200, value={"most_selling_products": products})


@statistics_routes.route("/<int:salesperson_id>/customers")
@jwt_required()
def customers_statistics(salesperson_id):
    customers = db.session.execute(
        text("CALL salesperson_customer_statistics(:salesperson_id)"),
        {"salesperson_id": salesperson_id},
    )
    customers = CustomerStatisticsSchema(many=True).dump(customers)
    return response_with(resp.SUCCESS_200, value={"customers_statistics": customers})


@statistics_routes.route("/orders/")
def month_vs_order_qty_by_customer_id():
    start_year = request.args.get("start_year")
    end_year = request.args.get("end_year")
    orders = db.session.execute(
        text("CALL month_vs_order_qty(:start_year, :end_year)"),
        {"start_year": start_year, "end_year": end_year},
    )
    return response_with(
        resp.SUCCESS_200,
        value={"month_vs_order_qty": MonthVsOrderQtySchema(many=True).dump(orders)},
    )

@statistics_routes.route("/payment_status/")
def payment_status_statistics():
    start_year = request.args.get("start_year")
    end_year = request.args.get("end_year")
    payments = db.session.execute(
        text("CALL payment_status_statistics(:start_year, :end_year)"),
        {"start_year": start_year, "end_year": end_year},
    )
    return response_with(
        resp.SUCCESS_200,
        value={"statistics": PaymentStatusStatisticsSchema(many=True).dump(payments)},
    )
