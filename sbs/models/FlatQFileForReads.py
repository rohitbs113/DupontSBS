from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class FlatQFileForReads(BaseModel):
    __tablename__ = 'FLAT_Q_FILE_FOR_READS'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    location = db.Column('LOCATION', db.String(50), nullable=True)

    #sample = db.relationship('Sample', uselist=False, backref='sample')


    def __init__(self, location):
        self.location = location

    def __repr__(self):
        return (
            "<id {}, location {}>").format(
            self.id,
            self.location)

    def as_dict(self):
        return {
            "id": self.id,
            "location": self.location
        }
