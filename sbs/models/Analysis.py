from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.dialects.mysql import BIGINT
from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db
import enum


class RequestType(enum.Enum):
    alpha = "Alpha"
    alphad = "AlphaD"
    delta = "Delta"


class Analysis(BaseModel):
    __tablename__ = 'ANALYSIS'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    input_map = db.Column('INPUT_MAP', db.String(20), nullable=True)
    type = db.Column('TYPE', db.Enum(RequestType))
    reference = db.Column('REFERENCE', db.String(20), nullable=True)
    job_status = db.Column('JOB_STATUS', db.String(20), nullable=True)
    sbs_status = db.Column('SBS_STATUS', db.String(50), nullable=True)
    sbs_version = db.Column('SBS_VERSION', db.String(50), nullable=True)
    pipeline_call = db.Column('PIPELINE_CALL', db.String(20), nullable=True)
    current_call = db.Column('CURRENT_CALL', db.String(20), nullable=True)
    geno_type = db.Column('GENO_TYPE', db.String(20), nullable=True)
    event_id = db.Column('EVENT_ID', db.String(20), nullable=True)
    backbone_call = db.Column('BACKBONE_CALL', db.String(20), nullable=True)
    released_on = db.Column('RELEASED_ON', db.String(20), nullable=True)
    sample_call = db.Column('SAMPLE_CALL', db.String(20), nullable=True)
    sbs_integ_tier = db.Column('SBS_INTEG_TIER', db.String(20), nullable=True)
    vqc_ali_pct = db.Column('VQC_ALI_PCT', db.String(20), nullable=True)
    is_deprecated = db.Column('IS_DEPRECATED', db.Boolean, default=False,
                              nullable=False)
    load_date = db.Column('LOAD_DATE', db.TIMESTAMP, nullable=True)
    is_visible_to_client = db.Column('IS_VISIBLE_TO_CLIENT', db.Boolean,
                                     default=False, nullable=False)
    single_read_count = db.Column('SINGLE_READ_COUNT', BIGINT(unsigned=True),
                                  nullable=True)
    paired_read_count = db.Column('PAIRED_READ_COUNT', BIGINT(unsigned=True),
                                  nullable=True)
    complete_probe_coverage = db.Column('COMPLETE_PROBE_COVERAGE', db.Boolean,
                                        default=False, nullable=False)
    target_rate = db.Column('ON_TARGET_RATE', db.String(20), nullable=True)
    tier_3_reason = db.Column('TIER_3_REASON', db.String(20), nullable=True)
    manual_set = db.Column('MANUAL_SET', db.String(50), nullable=True)
    call_comment = db.Column('CALL_COMMENT', db.String(50), nullable=True)

    sample_id = db.Column('SAMPLE_ID', INTEGER(unsigned=True), db.ForeignKey('SAMPLE.ID'))
    configuration_id = db.Column('CONFIGURATION_ID', INTEGER(unsigned=True),
                                 db.ForeignKey('PIPELINE_CONFIGURATION.ID'))
    sample = db.relationship('Sample', foreign_keys=sample_id, backref='analysis')
    error_id = db.relationship('Error', backref='analysis', lazy='dynamic')
    map_analysis = db.relationship('MapAnalysis', backref='analysis_map', lazy='dynamic')
    comments = db.relationship('AnalysisComment', backref='analysis', lazy='dynamic')
    #analysis_tools_details = db.relationship('AnalysisToolsDetails', backref='analysisToolsDetails', lazy='dynamic')

    def __init__(self, input_map, type, sample_id, reference, job_status,
                 sbs_status, sbs_version, pipeline_call, current_call,
                 geno_type, event_id, backbone_call, released_on, sample_call,
                 sbs_integ_tier, vqc_ali_pct, is_deprecated, load_date,
                 is_visible_to_client, single_read_count, paired_read_count,
                 complete_probe_coverage, target_rate, tier_3_reason,
                 manual_set, call_comment, configuration_id):
        self.input_map = input_map
        self.type = type
        self.sample_id = sample_id
        self.reference = reference
        self.job_status = job_status
        self.sbs_status = sbs_status
        self.sbs_version = sbs_version
        self.pipeline_call = pipeline_call
        self.current_call = current_call
        self.geno_type = geno_type
        self.event_id = event_id
        self.backbone_call = backbone_call
        self.released_on = released_on
        self.sample_call = sample_call
        self.sbs_integ_tier = sbs_integ_tier
        self.vqc_ali_pct = vqc_ali_pct
        self.is_deprecated = is_deprecated
        self.load_date = load_date
        self.is_visible_to_client = is_visible_to_client
        self.single_read_count = single_read_count
        self.paired_read_count = paired_read_count
        self.complete_probe_coverage = complete_probe_coverage
        self.target_rate = target_rate
        self.tier_3_reason = tier_3_reason
        self.manual_set = manual_set
        self.call_comment = call_comment
        self.configuration_id = configuration_id

    def __repr__(self):
        return (
            "<id {}, sample_id {}, event_id {}>").format(
            self.id,
            self.sample_id,
            self.event_id)

    def as_dict(self):
        return {
            "id": self.id,
            "input_map": self.input_map,
            "type": self.type,
            "sample_id": self.sample_id,
            "reference": self.reference,
            "job_status": self.job_status,
            "sbs_status": self.sbs_status,
            "sbs_version": self.sbs_version,
            "pipeline_call": self.pipeline_call,
            "current_call": self.current_call,
            "geno_type": self.geno_type,
            "event_id": self.event_id,
            "backbone_call": self.backbone_call,
            "released_on": self.released_on,
            "sample_call": self.sample_call,
            "sbs_integ_tier": self.sbs_integ_tier,
            "vqc_ali_pct": self.vqc_ali_pct,
            "is_deprecated": self.is_deprecated,
            "load_date": self.load_date,
            "is_visible_to_client": "true" if self.is_visible_to_client
                                    else "false",
            "single_read_count": self.single_read_count,
            "paired_read_count": self.paired_read_count,
            "complete_probe_coverage": self.complete_probe_coverage,
            "target_rate": self.target_rate,
            "tier_3_reason": self.tier_3_reason,
            "manual_set": self.manual_set,
            "call_comment": self.call_comment,
            "configuration_id": self.configuration_id
        }
