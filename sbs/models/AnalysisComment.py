from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class AnalysisComment(BaseModel):
    __tablename__ = 'ANALYSIS_COMMENT'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    comment = db.Column('COMMENT', db.String(1000), nullable=True)

    analysis_id = db.Column('ANALYSIS_ID', INTEGER(unsigned=True),
                            db.ForeignKey('ANALYSIS.ID'))

    def __init__(self, comment, analysis_id, created_by, updated_by):
        self.comment = comment
        self.analysis_id = analysis_id
        self.created_by = created_by
        self.updated_by = updated_by

    def __repr__(self):
        return (
            "<id {}, comment {}>").format(
            self.id,
            self.comment)

    def as_dict(self):
        return {
            "id": self.id,
            "comment": self.comment,
            "analysis_id": self.analysis_id,
            "created_on": self.created_on,
            "created_by": self.created_by
        }
