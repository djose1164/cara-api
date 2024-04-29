from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import text
from api.models.statistics import (
    CustomerStatisticsSchema,
    MonthVsOrderQtySchema,
    MostSellingSummary,
    PaymentStatusStatisticsSchema,
    PaymentSummary,
    ProductStatisticsSchema,
    RunningOuttaStocksSummary,
    SalesSummary,
)
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp

statistics_routes = Blueprint("statistics_routes", __name__)
START_DATE: str = "2021-01-01"

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
def product_statistics(salesperson_id):
    try:
        products = db.session.execute(
            text("CALL salesperson_product_statistics(:salesperson_id)"),
            {"salesperson_id": salesperson_id},
        )
        products = ProductStatisticsSchema(many=True).dump(products)
        return response_with(resp.SUCCESS_200, value={"most_selling_products": products})
    except Exception as e:
        print(e)
        return response_with(resp.SERVER_ERROR_500)


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
    payments = db.session.execute(
        text("CALL payment_status_statistics(:start_date, now())"),
        {"start_date": START_DATE},
    )
    return response_with(
        resp.SUCCESS_200,
        value={"statistics": PaymentStatusStatisticsSchema(many=True).dump(payments)},
    )


@statistics_routes.route("/summary/<int:salesperson_id>/")
def summary(salesperson_id: int):
    last_date = request.args.get("last_date")

    payment_status = db.session.execute(
        text("CALL payment_status_statistics(:last_date, now())"),
        {"last_date": last_date},
    )

    most_selling = db.session.execute(
        text("CALL most_selling_product(:last_date, now())"),
        {"last_date": last_date},
    ).first()

    latest_sales = db.session.execute(
        text("CALL latest_sales_in(:last_date, now())"),
        {"last_date": last_date},
    ).first()

    running_outta_stocks = db.session.execute(
        text("CALL products_running_outta_stocks(:salesperson_id)"),
        {"salesperson_id": salesperson_id},
    ).all()

    return response_with(
        resp.SUCCESS_200,
        value={
            "summary": {
                "payment_status": PaymentSummary(many=True).dump(payment_status),
                "most_selling": MostSellingSummary().dump(most_selling),
                "latest_sales": SalesSummary().dump(latest_sales),
                "running_outta_stocks": RunningOuttaStocksSummary(many=True).dump(running_outta_stocks),
            }
        },
    )
