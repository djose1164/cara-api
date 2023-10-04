from flask import Blueprint
from sqlalchemy import text
from api.models.statistics import CustomerStatisticsSchema, ProductStatisticsSchema
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp

statistics_routes = Blueprint("statistics_routes", __name__)


@statistics_routes.route("/")
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
