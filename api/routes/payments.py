from flask import request, Blueprint

from api.models.payments import Payment, PaymentSchema
import api.utils.responses as resp
from api.utils.responses import response_with


payment_routes = Blueprint("payment_routes", __name__)


@payment_routes.route("/")
def payment_index():
    fetched = Payment.query.all()
    fetched = PaymentSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"payments": fetched})
