from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class ObservedMapComment(BaseModel):
    __tablename__ = 'OBSERVED_MAP_COMMENT'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    comment = db.Column('COMMENT', db.String(1000), nullable=True)

    observed_map_id = db.Column('OBSERVED_MAP_ID', INTEGER(unsigned=True),
                                db.ForeignKey('OBSERVED_MAP.ID', ondelete='CASCADE', post_update=True))

    def __init__(self, comment, observed_map_id, created_by, updated_by):
        self.comment = comment
        self.observed_map_id = observed_map_id
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
            "observed_map_id": self.observed_map_id,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_on": self.created_on
        }
