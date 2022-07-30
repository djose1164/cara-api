"""
author:
    Daniel Victriano (@djose1164)
Copyright 2022 Cara

This module contains the user schema.
"""
from api.utils.database import db
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from passlib.hash import pbkdf2_sha256 as sha256
from marshmallow import fields


class User(db.Model):
    """
    Model class for user.

    Attributes:
        __tablename__ (str): Table for this model.
        id (int): User unique id.
        username (str): User's username.
        password (hash): User's password (encrypted).
        forename (str): User's first name.
        surname (str): User's last name.
        email (str): User's email.
        telephone (str): User's telephone.
    """

    __tablename__ = "users"
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    username = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(120), nullable=False)
    forename = db.Column(db.String(32))
    surname = db.Column(db.String(32))
    email = db.Column(db.String(64), nullable=False, unique=True)
    telephone = db.Column(db.String(11), unique=True)

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
        return cls.query.filter_by(email=email).first()

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


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

    id = fields.Integer(dump_only=True, load_only=True)
    forename = fields.String(required=True)
    surname = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(load_only=True)
