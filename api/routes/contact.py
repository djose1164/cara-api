from flask import request
from flask_restful import Resource
from api.models.address import AddressSchema, Address
from api.models.contact import Contact, ContactSchema
from api.models.customers import Customer
from api.models.users import User
import api.utils.responses as resp
from api.utils.responses import response_with
from api.utils.database import db


class ContactList(Resource):
    def put(self):
        if request.args.get("customer_id"):
            self.update_by_customer_id(request.args["customer_id"])
        elif request.args.get("user_id"):
            self.update_by_user_id(request.args["user_id"])
        else:
            return response_with(
                resp.BAD_REQUEST_400,
                message="Necesitas suministrar el customer_id o user_id como argumento.",
            )

    def update_by_customer_id(self, customer_id: int):
        customer = db.session.execute(
            db.select(Customer).filter_by(id=customer_id)
        ).scalar()

        contact = customer.contact
        if contact is None:
            contact = ContactSchema().load(request.json)
        else:
            ContactSchema().load(request.json, instance=contact)

        db.session.add(customer)
        db.session.commit()

        return response_with(resp.SUCCESS_200)

    def update_by_user_id(self, user_id: int):
        data = request.json
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()

        contact = user.contact
        if contact is None:
            print("Creating a new contact")
            contact = ContactSchema().load(request.json)
        else:
            print("We're updating the instance")
            print("address_id: ", contact.address_id)
            address_id = contact.address_id
            address_json = data.pop("address")
            contact = ContactSchema().load(data, instance=contact, session=db.session)
            address = db.get_or_404(Address, address_id)
            AddressSchema().load(address_json, instance=address, session=db.session)

        db.session.add(contact)
        db.session.commit()

        return response_with(resp.SUCCESS_200)
