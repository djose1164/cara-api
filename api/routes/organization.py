from flask import request
from flask_restful import Resource
from api.models.organization import Organization, OrganizationSchema

from api.utils.database import db
from api.utils.responses import response_with
import api.utils.responses as resp


class OrganizationListResource(Resource):
    def get(self):
        fetched = db.session.execute(db.select(Organization)).scalars()
        return response_with(
            resp.SUCCESS_200,
            value={"organizations": OrganizationSchema(many=True).dump(fetched)},
        )

    def post(self):
        data = request.json

        organizationSchema = OrganizationSchema(exclude=("members",))
        organization = organizationSchema.load(data)
        organization.create()

        return response_with(
            resp.SUCCESS_201,
            value={"organization": organizationSchema.dump(organization)},
        )


class OrganizationResource(Resource):
    def get(self, identifier: int):
        fetched = db.get_or_404(Organization, identifier)
        return response_with(
            resp.SUCCESS_200, value={"organization": OrganizationSchema(exclude=("members",)).dump(fetched)}
        )

