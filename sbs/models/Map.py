from sqlalchemy.dialects.mysql import INTEGER

from sbs.database_utility import db
from sbs.models.BaseModel import BaseModel


class Map(BaseModel):
    __tablename__ = 'MAP'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    construct_id = db.Column('CONSTRUCT_ID', db.String(50), nullable=True)
    pipeline_detail = db.Column('PIPELINE_DETAIL', db.Text, nullable=True)
    custom_pipeline_detail = db.Column('CUSTOM_PIPELINE_DETAIL', db.Text,
                                       nullable=True)
    map_analysis = db.relationship('MapAnalysis', backref='maps_map_analysis',
                                   lazy='dynamic')
    map_observed = db.relationship('ObservedMap', backref='maps_observed_map',
                                   lazy='dynamic')
    obs_map_version = 1

    def __init__(self, construct_id, pipeline_detail=None,
                 custom_pipeline_details=None):
        self.construct_id = construct_id
        self.pipeline_detail = pipeline_detail
        self.custom_pipeline_detail = custom_pipeline_details

    def __repr__(self):
        return (
            "<id {}, construct_id {}>").format(
            self.id,
            self.construct_id)

    def as_dict(self):
        return {
            "id": self.id,
            "construct_id": self.construct_id,
            "pipeline_detail": self.pipeline_detail,
            "custom_pipeline_detail": self.custom_pipeline_detail
        }
