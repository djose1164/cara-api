from flask import Blueprint
from sqlalchemy import text
from api.models.order_details import OrderDetail, OrderDetailSchema
from api.models.products import Product
from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp

statistics_routes = Blueprint("statistics_routes", __name__)


@statistics_routes.route("/")
def index():
    products = db.session.execute(text("CALL most_selling_products()"))
    unpaid_bills = db.session.execute(text("SELECT * FROM customers_with_unpaid_bills"))

    return response_with(
        resp.SUCCESS_200,
        value={
            "statistics": {
                "most_selling_products": [
                    {
                        "quantity": product[0],
                        "name": product[1],
                        "product_id": product[2],
                        "image_url": product[3],
                    }
                    for product in products
                ],
                "unpaid_bills": [
                    {"name": bill[0], "customer_id": bill[1], "bill_quantity": bill[2]}
                    for bill in unpaid_bills
                ],
            }
        },
    )
