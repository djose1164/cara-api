from flask import request, Blueprint
from flask_jwt_extended import jwt_required
from api.models.payment_detail import PaymentDetail

from api.models.payments import Payment, PaymentSchema
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db

payment_routes = Blueprint("payment_routes", __name__)


@payment_routes.route("/")
@jwt_required()
def payment_index():
    fetched = Payment.query.all()
    fetched = PaymentSchema(many=True).dump(fetched)
    return response_with(resp.SUCCESS_200, value={"payments": fetched})

@payment_routes.route("/<int:identifier>")
@jwt_required()
def payment_by_id(identifier: int):
    fetched = Payment.find_by_id(identifier)
    fetched = PaymentSchema().dump(fetched)
    return response_with(resp.SUCCESS_200, value={"payment": fetched})


@payment_routes.route("/", methods=["PATCH"])
@jwt_required()
def update_payment():
    try:
        data = request.get_json()
        fetched: Payment = Payment.find_by_id(data["id"])

        if data["paid_amount"] > fetched.amount_to_pay:
            return response_with(
                resp.BAD_REQUEST_400, message="La cantidad pagada supera la deuda."
            )
        elif data["paid_amount"] < 0:
            return response_with(
                resp.BAD_REQUEST_400,
                message="El nuevo monto pagado no puede ser menor que 0.",
            )

        fetched.paid_amount = data["paid_amount"]
        fetched.set_payment_status()

        db.session.add(fetched)
        db.session.commit()
        return resp.response_with(resp.SUCCESS_200)
    except Exception as e:
        print(e)
        return resp.response_with(resp.SERVER_ERROR_404)


@payment_routes.route("/<int:payment_id>", methods=["POST"])
@jwt_required()
def new_payment_detail(payment_id: int):
    try:
        data = request.json
        if data.get("amount") is None:
            return response_with(resp.BAD_REQUEST_400, error={"details": "amount is missing."})
        
        amount: int = data["amount"]
        if amount < 1:
            return response_with(resp.BAD_REQUEST_400, error={"details": "amount must be non-negative."})
        
        payment = Payment.find_by_id(payment_id)
        if payment.is_paid():
            return response_with(resp.SERVER_ERROR_500, error={"details": "Can't continue paying this bill; it's already paid."})
        elif payment.paid_amount  + amount > payment.amount_to_pay:
            return response_with(resp.SERVER_ERROR_500, error={"details": f"The amount is too big for the debt. amount: {amount} -- remaining debt: {payment.amount_to_pay - payment.paid_amount}"})
        
        payment_detail = PaymentDetail(payment_id=payment_id, amount=amount)
        payment.payment_details.append(payment_detail)
        payment.update_paid_amount()
        payment.set_payment_status()
        payment.create()

        return response_with(resp.SUCCESS_200, value={"payment": PaymentSchema().dump(payment)})
    except Exception as e:
        print(e)
        return response_with(resp.BAD_REQUEST_400)
