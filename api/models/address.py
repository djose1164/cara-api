from marshmallow_sqlalchemy import SQLAlchemyAutoSchema, auto_field
from marshmallow import fields

from api.utils.database import db


class Country(db.Model):
    __tablename__ = "country"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)


class CountrySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Country
        load_instance = True
        sqla_session = db.session


class Province(db.Model):
    __tablename__ = "province"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"))


class ProvinceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Province
        load_instance = True
        sqla_session = db.session


class Municipality(db.Model):
    __tablename__ = "municipality"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey("province.id"))


class MunicipalitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Municipality
        load_instance = True
        sqla_session = db.session


class Sector(db.Model):
    __tablename__ = "sector"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False)
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipality.id"))


class SectorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Sector
        load_instance = True
        sqla_session = db.session


class Address(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    country_id = db.Column(db.Integer, db.ForeignKey("country.id"))
    province_id = db.Column(db.Integer, db.ForeignKey("province.id"))
    municipality_id = db.Column(db.Integer, db.ForeignKey("municipality.id"))
    sector_id = db.Column(db.Integer, db.ForeignKey("sector.id"))
    street = db.Column(db.String(64))
    house_number = db.Column(db.Integer)
    country = db.relationship("Country", backref="country")
    province = db.relationship("Province", backref="province")
    municipality = db.relationship("Municipality", backref="municipality")
    sector = db.relationship("Sector", backref="sector")


class AddressSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Address
        load_instance = True
        sqla_session = db.session

    country_id = auto_field(required=True)
    province_id = auto_field(required=True)
    municipality_id = auto_field(required=True)
    sector_id = auto_field(required=True)
