from sqlalchemy.dialects.mysql import INTEGER

from sbs.database_utility import db
from sbs.models.BaseModel import BaseModel


class EndogenousJunctionSet(BaseModel):
    __tablename__ = 'ENDOGENOUS_JUNCTION_SET'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    crop_id = db.Column('CROP_ID', INTEGER(unsigned=True),
                        db.ForeignKey('CROP.ID'))
    name = db.Column('NAME', db.String(500), nullable=True)

    endogenous_junctions = db.relationship('EndogenousJunction',
                                           backref='endogenous_junction_set',
                                           lazy='dynamic')

    def __init__(self, crop_id, name):
        self.crop_id = crop_id
        self.name = name

    def __repr__(self):
        return (
            "<id {}, name {}, crop_id {}>").format(
            self.id,
            self.name,
            self.crop_id
        )

    def as_dict(self):
        return {
            "id": self.id,
            "crop_id": self.crop_id,
            "name": self.name
        }
