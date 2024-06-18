"""
author:
    Daniel Victriano (@djose1164)
Copyright 2022 Cara

This module contains the user schema.
"""

from enum import IntEnum
import random
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from passlib.hash import pbkdf2_sha256 as sha256
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import RAISE, fields
from api.models.contact import Contact
from api.models.person import PersonSchema
from api.models.salesperson import SalespersonSchema

from api.utils.database import db

class UserTypeEnum(IntEnum):
    ADMIN = 1
    CUSTOMER = 2
    ASSOCIATE_SALESPERSON = 3

class User(db.Model):
    """
    Model class for user.

    Attributes:
        __tablename__ (str): Table for this model.
        id (int): User unique id.
        username (str): User's username.
        password (hash): User's password (encrypted).
        email (str): User's email.
        user_type_id (int): Define the type of ths user.
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    username = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(120), nullable=False)
    user_type_id = db.Column(db.Integer, nullable=False, default=2)
    person_id = db.Column(db.Integer, db.ForeignKey("person.id"), nullable=False)
    person = db.relationship("Person", backref="user", uselist=False)
    salesperson = db.relationship(
        "Salesperson",
        backref="user",
        uselist=False,
        primaryjoin="Salesperson.user_id == User.id",
    )
    associated_salespersons = db.relationship(
        "Salesperson", primaryjoin="Salesperson.admin_id == User.id"
    )
    customer = db.relationship("Customer", backref="user", uselist=False)

    def __init__(self, username, password, user_type_id, person) -> None:
        self.username = username
        self.password = self.generate_hash(password)
        self.user_type_id = user_type_id
        self.person = person


    def create(self):
        """
        Create an new user by adding it to the database.

        Returns:
            The recently created user.
        """
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_id(cls, userId):
        """
        Find the user by its id.
        """
        return cls.query.filter_by(id=userId).first_or_404()

    @classmethod
    def find_by_username(cls, username):
        """
        Find the user by its username.
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        """
        Find the user by its email.
        """
        return cls.query.join(Contact).filter(Contact.email == email).first()

    @staticmethod
    def get_by_id(admin_id: int) -> "User":
        return db.get_or_404(User, admin_id)

    def is_admin(self) -> bool:
        return self.user_type_id == 1

    def is_customer(self) -> bool:
        return self.user_type_id == 2

    def is_salesperson(self) -> bool:
        return self.user_type_id == 3

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)

    def generate_username(self, fullname):
        self.username = User.specific_string(fullname)

    @staticmethod
    def specific_string(fullname):
        # define the condition for random string
        return "".join((random.choice(fullname)) for x in range(16))
    
    @staticmethod
    def delete_by_id(user_id: int):
        user = db.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit();


class UserSchema(SQLAlchemyAutoSchema):
    """
    Schema for serializing and deserializing user instances.

    Attributes:
        username (str): Expose user's username.
        email (str): Expose user's email.
        forename (str): Expose user's first name.
        surname (str): Expose user's last name.
    """

    class Meta:
        model = User
        sqla_session = db.session
        load_instance = True

    id = auto_field(dump_only=True)
    password = auto_field(load_only=True)
    user_type_id = auto_field(load_default=int(UserTypeEnum.CUSTOMER))
    person = fields.Nested(PersonSchema)
    salesperson = fields.Nested(
        "SalespersonSchema", exclude=("user", "buy_orders", "inventory", "customers")
    )
    associated_salesperson = fields.Nested(
        "SalespersonSchema", many=True, exclude=("user",)
    )
    favorites = fields.List(fields.Nested("FavoriteProductSchema"))
    customer = fields.Nested(
        "CustomerSchema", dump_only=True, exclude=("orders",), #metadata={"partial": True}
    )
    forename = fields.String(attribute="person.forename", dump_only=True)
    surname = fields.String(attribute="person.surname", dump_only=True)
