from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class Crop(BaseModel):
    __tablename__ = 'CROP'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    organism = db.Column('ORGANISM', db.String(20), nullable=True)

    request_id = db.relationship('Request', backref='crop', lazy='dynamic')
    #endogenousJunctionSet = db.relationship('EndogenousJunctionSet', backref='endogenousJunctionSet', lazy='dynamic')

    def __init__(self, organism):
        self.organism = organism

    def __repr__(self):
        return (
            "<id {}, organism {}>").format(
            self.id,
            self.organism)

    def as_dict(self):
        return {
            "id": self.id,
            "organism": self.organism
        }
