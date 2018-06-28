from sqlalchemy.dialects.mysql import INTEGER
from sbs.database_utility import db


class MapAnalysisJunctions(db.Model):
    __tablename__ = 'MAP_ANALYSIS_JUNCTIONS'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)

    map_analysis_id = db.Column('MAP_ANALYSIS_ID', INTEGER(unsigned=True),
                                db.ForeignKey('MAP_ANALYSIS.ID'))
    junction_id = db.Column('JUNCTION_ID', INTEGER(unsigned=True),
                            db.ForeignKey('JUNCTION.ID'))

    junction = db.relationship('Junction', backref='junctions', lazy=True)

    masked = db.Column('MASKED', db.Boolean, default=False, nullable=False)
    junction_comment = db.Column('COMMENT', db.String(500), nullable=True)
    masked_by = db.Column('COMMENTED_BY', db.String(50), db.ForeignKey('USER_ROLE.USERNAME'), default='system',
              nullable=True)

    def __init__(self, map_analysis_id, junction_id, masked, junction_comment, masked_by):
        self.map_analysis_id = map_analysis_id
        self.junction_id = junction_id
        self.masked = masked
        self.junction_comment = junction_comment
        self.masked_by = masked_by

    def __repr__(self):
        return (
            "<id {}, map_analysis_id {}, junction_id {}, masked {}, junction_comment {}, masked_by {}").format(
            self.id,
            self.map_analysis_id,
            self.junction_id,
            self.masked,
            self.junction_comment,
            self.masked_by
        )

    def as_dict(self):
        return {
            "id": self.id,
            "map_analysis_id": self.map_analysis_id,
            "junction_id": self.junction_id,
            "masked": self.masked,
            "junction_comment": self.junction_comment,
            "masked_by": self.masked_by
        }
