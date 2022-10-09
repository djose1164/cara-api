from flask import request, Blueprint

from api.models.payments import Payment, PaymentSchema
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

payment_routes = Blueprint("payment_routes", __name__)


@payment_routes.route("/")
def payment_index():
    fetched = Payment.query.all()
    fetched = PaymentSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"payments": fetched})


@payment_routes.route("/", methods=["PATCH"])
def update_payment():
    try:
        data = request.get_json()
        fetched = Payment.find_by_id(data["id"])
        
        if data["paid_amount"] > fetched.amount_to_pay:
            return response_with(
                resp.BAD_REQUEST_400, message="La cantidad pagada supera la deuda."
            )
        elif data["paid_amount"] < 0:
            return response_with(resp.BAD_REQUEST_400, message="El nuevo monto pagado no puede ser menor que 0.")
        
        fetched.paid_amount = data["paid_amount"]
        
        db.session.add(fetched)
        db.session.commit()
        return resp.response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return resp.response_with(resp.SERVER_ERROR_404)
