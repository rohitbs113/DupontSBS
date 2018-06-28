from sqlalchemy.dialects.mysql import INTEGER

from sbs.database_utility import db
from sbs.models.BaseModel import BaseModel


class PipelineConfiguration(BaseModel):
    __tablename__ = 'PIPELINE_CONFIGURATION'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True,
                   unique=True)
    name = db.Column('NAME', db.String(100), nullable=False)
    endogenous_set = db.Column('ENDOGENOUS_SET', db.String(500), nullable=False)
    version = db.Column('VERSION', INTEGER(unsigned=True), nullable=False)
    conf_file = db.Column('CONF_FILE', db.Text, nullable=True)

    analysis_config = db.relationship('Analysis', backref='pipeline_config', lazy='dynamic')

    def __init__(self, name, version, conf_file, endogenous_set):
        self.name = name
        self.version = version
        self.conf_file = conf_file
        self.endogenous_set = endogenous_set

    def __repr__(self):
        return (
            "<id {}, name {}, version {}>").format(
            self.id,
            self.name,
            self.version
        )

    def as_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "endogenous_set": self.endogenous_set,
            "version": self.version,
            "conf_file": self.conf_file,
            "created_on": self.created_on
        }
