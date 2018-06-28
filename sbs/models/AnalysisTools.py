from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class AnalysisTools(BaseModel):
    __tablename__ = 'ANALYSIS_TOOLS'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    name = db.Column('NAME', db.String(100), nullable=False)

    analysis_tools_details = db.relationship('AnalysisToolsDetails', backref='tools_details_analysis_tools', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return (
            "<id {}, name {}>").format(
            self.id,
            self.name)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }
