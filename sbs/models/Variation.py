from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.dialects.mysql import DECIMAL

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class Variation(BaseModel):
    __tablename__ = 'VARIATION'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    position = db.Column('POSITION', BIGINT(unsigned=True), nullable=True)
    type = db.Column('TYPE', db.String(10), nullable=True)
    ref_base = db.Column('REF_BASE', db.String(100), nullable=True)
    sample_base = db.Column('SAMPLE_BASE', db.String(100), nullable=True)
    translation = db.Column('TRANSLATION', db.String(200), nullable=True)
    coverage = db.Column('COVERAGE', BIGINT(unsigned=True), nullable=True)
    purity = db.Column('PURITY', DECIMAL(6,5), nullable=True)
    tier = db.Column('TIER', db.String(20), nullable=True)
    read_depth = db.Column('READ_DEPTH', db.String(20), nullable=True)
    annotation = db.Column('ANNOTATION', db.String(100), nullable=True)
    tier_label = db.Column('TIER_LABEL', db.String(20), nullable=True)
    gt = db.Column('GT', db.String(20), nullable=True)
    total_read_depth = db.Column('TOTAL_READ_DEPTH', db.String(20), nullable=True)
    feature_type = db.Column('FEATURE_TYPE', db.String(50), nullable=True)
    effects = db.Column('EFFECTS', db.String(50), nullable=True)
    organism = db.Column('ORGANISM', db.String(20), nullable=True)
    is_tier_label_updated = db.Column('IS_TIER_LABEL_UPDATED', db.Boolean,
                                      default=False, nullable=False)

    map_analysis_id = db.Column('MAP_ANALYSIS_ID', INTEGER(unsigned=True),
                                db.ForeignKey('MAP_ANALYSIS.ID'))

    construct_id = None
    sample_id = None
    lab_name = None
    def __init__(self, position, type, ref_base, sample_base, translation,
                 coverage, purity, tier, read_depth, annotation, tier_label,
                 is_tier_label_updated, gt, total_read_depth, feature_type, 
                 effects, organism, map_analysis_id):
        self.position = position
        self.type = type
        self.ref_base = ref_base
        self.sample_base = sample_base
        self.translation = translation
        self.coverage = coverage
        self.purity = purity
        self.tier = tier
        self.read_depth = read_depth
        self.annotation = annotation
        self.tier_label = tier_label
        self.is_tier_label_updated = is_tier_label_updated
        self.gt = gt
        self.total_read_depth = total_read_depth
        self.feature_type = feature_type
        self.effects = effects
        self.organism = organism
        self.map_analysis_id = map_analysis_id

    def __repr__(self):
        return (
            "<id {}, type {}, tier {}, annotation {}, tier_label {}>").format(
            self.id,
            self.type,
            self.tier,
            self.annotation,
            self.tier_label)

    def as_dict(self):
        return {
            "id": self.id,
            "sample_id": self.sample_id,
            "lab_name": self.lab_name,
            "position": self.position,
            "type": self.type,
            "ref_base": self.ref_base,
            "sample_base": self.sample_base,
            "translation": self.translation,
            "coverage": self.coverage,
            "purity": self.purity,
            "tier": self.tier,
            "read_depth": self.read_depth,
            "annotation": self.annotation,
            "tier_label": self.tier_label,
            "gt": self.gt,
            "total_read_depth": self.total_read_depth,
            "feature_type": self.feature_type,
            "effects": self.effects,
            "organism": self.organism,
            "map_analysis_id": self.map_analysis_id,
            "construct_id": self.construct_id,
            "is_tier_label_updated": "true" if self.is_tier_label_updated
                                     else "false"
        }
