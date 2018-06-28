from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class Request(BaseModel):
    __tablename__ = 'REQUEST'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    request_id = db.Column('REQUEST_ID', db.String(50), nullable=True)
    sample_prep_methods = db.Column('SAMPLE_PREP_METHODS', db.String(20), nullable=True)
    sbs_internalpipeline_version = db.Column('SBS_INTERNALPIPELINE_VERSION', db.String(20), nullable=True)
    request_name = db.Column('REQUEST_NAME', db.String(20), nullable=True)
    released_on = db.Column('RELEASED_ON', db.TIMESTAMP, default=db.func.now(), nullable=False)
    sbs_status = db.Column('SBS_STATUS', db.String(20), nullable=True)
    researcher = db.Column('RESEARCHER', db.String(50), nullable=True)

    tx_method_id = db.Column('TX_METHOD', INTEGER(unsigned=True), db.ForeignKey('TX_METHOD.ID'))
    organism_id = db.Column('ORGANISM', INTEGER(unsigned=True), db.ForeignKey('CROP.ID'))

    samples = db.relationship('Sample', backref='request', lazy='dynamic')
    request_comment = db.relationship('RequestComment', backref='requests', lazy='dynamic')

    load_date = ""
    tx_method = ""
    sample_type = ""
    organism = ""
    alpha_samples, delta_samples, total_comments, total_errors, total_samples = (0, 0, 0, 0, 0)

    def __init__(self, request_id, sample_prep_methods,
                 sbs_internalpipeline_version, request_name, released_on,
                 sbs_status, researcher, tx_method_id, organism_id):
        self.request_id = request_id
        self.organism_id = organism_id
        self.sample_prep_methods = sample_prep_methods
        self.sbs_internalpipeline_version = sbs_internalpipeline_version
        self.request_name = request_name
        self.released_on = released_on
        self.sbs_status = sbs_status
        self.researcher = researcher
        self.tx_method_id = tx_method_id

    def __repr__(self):
        return (
            "<id {}, request_id {}, sbs_internalpipeline_version {}, "
            "request_name {}>").format(
            self.id,
            self.request_id,
            self.sbs_internalpipeline_version,
            self.request_name)

    def as_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "sample_prep_methods": self.sample_prep_methods,
            "sbs_internalpipeline_version": self.sbs_internalpipeline_version,
            "sbs_status": self.sbs_status,
            "request_name": self.request_name,
            "released_on": self.released_on,
            "researcher": self.researcher,
            "tx_method_id": self.tx_method_id,
            "organism_id": self.organism_id
        }

    def browse_request_as_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "alpha_samples": self.alpha_samples if self.alpha_samples else '',
            "delta_samples": self.delta_samples if self.delta_samples else '',
            "sbs_internalpipeline_version": self.sbs_internalpipeline_version,
            "request_name": self.request_name,
            "status": self.sbs_status if self.sbs_status else '',
            "researcher": self.researcher if self.researcher else '',
            "load_date": self.load_date if self.load_date else '',
            "tx_method": self.tx_method if self.tx_method else '',
            "organism": self.organism if self.organism else '',
            "tx_method_id": self.tx_method_id,
            "total_comments": self.total_comments,
            "total_errors": self.total_errors
        }

    def browse_request_client_as_dict(self):
        return {
            "id": self.id,
            "request_id": self.request_id,
            "request_name": self.request_name,
            "status": self.sbs_status if self.sbs_status else '',
            "researcher": self.researcher if self.researcher else '',
            "load_date": self.load_date if self.load_date else '',
            "tx_method": self.tx_method if self.tx_method else '',
            "organism": self.organism if self.organism else '',
            "tx_method_id": self.tx_method_id,
            "total_samples": self.total_samples
        }
