from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class Error(BaseModel):
    __tablename__ = 'ERROR'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    error = db.Column('ERROR', db.String(1000), nullable=True)

    analysis_id = db.Column('ANALYSIS_ID', INTEGER(unsigned=True),
                            db.ForeignKey('ANALYSIS.ID'))

    def __init__(self, error, analysis_id):
        self.error = error
        self.analysis_id = analysis_id

    def __repr__(self):
        return (
            "<id {}, error {}>").format(
            self.id,
            self.error
        )

    def as_dict(self):
        return {
            "id": self.id,
            "error": self.error,
            "analysis_id": self.analysis_id
        }
