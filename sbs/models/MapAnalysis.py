from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class MapAnalysis(BaseModel):
    __tablename__ = 'MAP_ANALYSIS'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    read_count = db.Column('READ_COUNT', db.String(50), nullable=True)

    analysis_id = db.Column('ANALYSIS_ID', INTEGER(unsigned=True),
                            db.ForeignKey('ANALYSIS.ID'))
    map_id = db.Column('MAP_ID', INTEGER(unsigned=True),
                       db.ForeignKey('MAP.ID'))

    variation = db.relationship('Variation', backref='vars_mapanalysis', lazy='dynamic')
    map_analysis_junctions = db.relationship('MapAnalysisJunctions', backref='junctions_mapanalysis', lazy='dynamic')

    def __init__(self, read_count, analysis_id, map_id):
        self.read_count = read_count
        self.analysis_id = analysis_id
        self.map_id = map_id

    def __repr__(self):
        return (
            "<id {}, read_count {}>").format(
            self.id,
            self.read_count
        )

    def as_dict(self):
        return {
            "id": self.id,
            "error": self.read_count,
            "analysis_id": self.analysis_id,
            "map_id": self.map_id
        }
