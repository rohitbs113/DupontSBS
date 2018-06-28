from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class TxMethod(BaseModel):
    __tablename__ = 'TX_METHOD'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    method_name = db.Column('METHOD_NAME', db.String(50), nullable=True)

    request_id = db.relationship('Request', backref='txmethod', lazy='dynamic')

    def __init__(self, method_name):
        self.method_name = method_name

    def __repr__(self):
        return (
            "<id {}, method_name {}>").format(
            self.id,
            self.method_name)

    def as_dict(self):
        return {
            "id": self.id,
            "method_name": self.method_name
        }
