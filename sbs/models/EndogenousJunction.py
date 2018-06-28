from sqlalchemy.dialects.mysql import INTEGER

from sbs.database_utility import db
from sbs.models.BaseModel import BaseModel
from sbs.models.EndogenousJunctionSet import EndogenousJunctionSet
from sbs.models.Junction import Junction


class EndogenousJunction(BaseModel):
    __tablename__ = 'ENDOGENOUS_JUNCTION'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    junction_set = db.Column('JUNCTION_SET', INTEGER(unsigned=True),
                             db.ForeignKey(EndogenousJunctionSet.id))
    junction_id = db.Column('JUNCTION_ID', INTEGER(unsigned=True),
                            db.ForeignKey(Junction.id))

    def __init__(self, junction_set, junction_id):
        self.junction_set = junction_set
        self.junction_id = junction_id

    def __repr__(self):
        return (
            "<id {}, junction_set {}>").format(
            self.id,
            self.junction_set
        )

    def as_dict(self):
        return {
            "id": self.id,
            "junction_id": self.junction_id,
            "junction_set": self.junction_set
        }
