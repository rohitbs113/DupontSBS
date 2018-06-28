from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.dialects.mysql import BIGINT

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class ObservedMap(BaseModel):
    __tablename__ = 'OBSERVED_MAP'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    name = db.Column('NAME', db.String(50), nullable=True)
    load_time = db.Column('LOAD_TIME', db.TIMESTAMP, nullable=False)
    length = db.Column('LENGTH', BIGINT(unsigned=True), nullable=True)
    status = db.Column('STATUS', db.String(50), nullable=True)
    send_to_evman = db.Column('SEND_TO_EVMAN', db.Boolean, default=False,
                              nullable=False)
    version = db.Column('VERSION', BIGINT(unsigned=True), nullable=True)

    map_id = db.Column('MAP_ID', INTEGER(unsigned=True),
                       db.ForeignKey('MAP.ID'))
    comments = db.relationship('ObservedMapComment',
                               backref='comment_observed_map', lazy='dynamic',
                               passive_deletes=True)

    run_id = "1"
    sample_id = None
    analysis_id = None
    sample_name = None
    event_id = None
    analysis_type = None
    map_name = None
    construct_id = None

    def __init__(self, name, load_time, length, status, send_to_evman,
                 map_id, version):
        self.name = name
        self.load_time = load_time
        self.length = length
        self.status = status
        self.send_to_evman = send_to_evman
        self.map_id = map_id
        self.version = version

    def __repr__(self):
        return (
            "<id {}, name {}>").format(
            self.id,
            self.name)

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "load_time": self.load_time,
            "length": self.length,
            "status": self.status,
            "send_to_evman": self.send_to_evman,
            "map_id": self.map_id,
            "construct_id": self.construct_id,
            "sample_id":  self.sample_id,
            "analysis_id":  self.analysis_id,
            "version":  self.version
        }

    def browse_as_dict(self):
        return {
            "id": self.id,
            "name": self.name if self.name else '',
            "load_time": str(self.load_time),
            "length": self.length if self.length else '',
            "status": self.status if self.status else '',
            "send_to_evman":  self.send_to_evman,
            "map_id": self.map_id if self.map_id else '',
            "sample_id":  self.sample_id if self.sample_id else '',
            "sample_name": self.sample_name if self.sample_name else '',
            "event_id": self.event_id if self.event_id else '',
            "analysis_type": self.analysis_type if self.analysis_type else '',
            "run_id": self.run_id if self.run_id else '',
            "modified_time": str(self.updated_on),
            "map_name": self.map_name if self.map_name else '',
            "version": self.version
        }
