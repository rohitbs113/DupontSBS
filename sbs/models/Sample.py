from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class Sample(BaseModel):
    __tablename__ = 'SAMPLE'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    sample_id = db.Column('SAMPLE_ID', db.String(50), nullable=True)
    primary_map = db.Column('PRIMARY_MAP', db.String(50), nullable=True)
    ev_man_event = db.Column('EV_MAN_EVENT', db.String(50), nullable=True)
    other_maps = db.Column('OTHER_MAPS', db.String(50), nullable=True)
    construct_name = db.Column('CONSTRUCT_NAME', db.String(50), nullable=True)
    event_id = db.Column('EVENT_ID', db.String(20), nullable=True)
    geno_type = db.Column('GENO_TYPE', db.String(500), nullable=True)
    organism = db.Column('ORGANISM', db.String(20), nullable=True)
    sample_name = db.Column('SAMPLE_NAME', db.String(20), nullable=True)
    develop_stage = db.Column('DEVELOP_STAGE', db.String(20), nullable=True)
    growth_location = db.Column('GROWTH_LOCATION', db.String(50), nullable=True)
    treated = db.Column('TREATED', db.Boolean, default=False, nullable=False)
    eu_id = db.Column('EU_ID', db.String(50), nullable=True)

    request_id = db.Column('REQUEST_ID', INTEGER(unsigned=True), db.ForeignKey('REQUEST.ID'))
    curr_alpha_analysis = db.Column('CURR_ALPHA_ANALYSIS', INTEGER(unsigned=True),
                                    db.ForeignKey('ANALYSIS.ID', use_alter=True, name='fk_sample_analysis_id'))
    curr_alpha = db.relationship('Analysis', foreign_keys=curr_alpha_analysis, post_update=True)
    # reads = db.Column('READS', INTEGER(unsigned=True), db.ForeignKey('FLAT_Q_FILE_FOR_READS.ID'))

    pipeline_call = ""
    current_call = ""
    status = ""
    load_date = ""
    type = ""
    is_visible = ""
    analysis_id = None
    total_maps, total_errors, total_varitaions, total_samples = (0, 0, 0, 0)
    single_read_count = None
    paired_read_count = None
    complete_probe_coverage = ""
    target_rate = ""
    tier_3_reason = ""
    sbs_version = ""
    reference = ""
    observed_map_id = None
    construct_ids = {}
    analysis_geno_type = ""
    backbone_call = ""
    analysis_event_id = ""
    req_id = ""
    request_name = ""
    researcher = ""
    request_organism = ""
    comments = {}
    manual_set = ""
    call_comment = ""
    total_pending_maps = 0
    configuration_id = None

    def __init__(self, sample_id, primary_map, ev_man_event, other_maps,
                 request_id, construct_name, event_id, geno_type, organism,
                 sample_name, develop_stage, growth_location, treated, eu_id,
                 curr_alpha_analysis):
        self.sample_id = sample_id
        self.primary_map = primary_map
        self.ev_man_event = ev_man_event
        self.other_maps = other_maps
        self.request_id = request_id
        self.construct_name = construct_name
        self.event_id = event_id
        self.geno_type = geno_type
        self.organism = organism
        self.sample_name = sample_name
        self.develop_stage = develop_stage
        self.growth_location = growth_location
        self.treated = treated
        self.eu_id = eu_id
        self.curr_alpha_analysis = curr_alpha_analysis
        # self.reads = reads

    def __repr__(self):
        return (
            "<id {}, event_id {}, request_id {}>").format(
            self.id,
            self.event_id,
            self.request_id)

    def as_dict(self):
        return {
            "id": self.id,
            "sample_id": self.sample_id,
            "primary_map": self.primary_map,
            "other_maps": self.other_maps,
            "request_id": self.request_id,
            "construct_name": self.construct_name,
            "event_id": self.event_id,
            "geno_type": self.geno_type,
            "organism": self.organism,
            "sample_name": self.sample_name,
            "develop_stage": self.develop_stage,
            "growth_location": self.growth_location,
            "treated": self.treated,
            "eu_id": self.eu_id,
            "curr_alpha_analysis": self.curr_alpha_analysis
        }

    def browse_sample_as_dict(self):
        return {
            "id": self.id,
            "analysis_id": self.analysis_id,
            "sample_id": self.sample_id,
            "sample_name": self.sample_name,
            "construct_name": self.construct_name,
            "event_id": self.event_id,
            "geno_type": self.geno_type,
            "eu_id": self.eu_id,
            "develop_stage": self.develop_stage,
            "curr_alpha_analysis": self.curr_alpha_analysis,
            "pipeline_call": self.pipeline_call if self.pipeline_call else '',
            "current_call": self.current_call if self.current_call else '',
            "status": self.status if self.status else '',
            "load_date": self.load_date,
            "type": str(self.type.value) if self.type else "",
            "is_visible_to_cilent": "Yes" if self.is_visible else "No",
            "total_variations": self.total_variations,
            "total_maps": self.total_maps,
            "total_errors": self.total_errors if self.total_maps else 0,
            "single_read_count": self.single_read_count,
            "paired_read_count": self.paired_read_count,
            "complete_probe_coverage": self.complete_probe_coverage,
            "target_rate": self.target_rate,
            "tier_3_reason": self.tier_3_reason,
            "sbs_version": self.sbs_version,
            "modified_date": self.updated_on,
            "reference_genome": self.reference,
            "observed_map_id": self.observed_map_id,
            "construct_ids": self.construct_ids,
            "analysis_geno_type": self.analysis_geno_type,
            "backbone_call": self.backbone_call,
            "analysis_event_id": self.analysis_event_id,
            "request_id": self.req_id,
            "researcher": self.researcher,
            "request_name": self.request_name,
            "request_date": "",
            "organism": self.request_organism,
            "comments": self.comments,
            "Department": "",
            "department": "",
            "read_count": "",
            "endogenous_set": "",
            "expected_php": "",
            "experiment_summary": "",
            "lab_name": "",
            "manual_set": self.manual_set if self.manual_set else '',
            "call_comment": self.call_comment if self.call_comment else '',
            "total_pending_maps": self.total_pending_maps if self.total_pending_maps else 0,
            "configuration_id": self.configuration_id
        }
