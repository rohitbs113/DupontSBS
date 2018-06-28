from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.dialects.mysql import BIGINT
from sbs.database_utility import db
from sbs.models.BaseModel import BaseModel


class Junction(BaseModel):
    __tablename__ = 'JUNCTION'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    end = db.Column('END', db.String(50), nullable=True)
    position = db.Column('POSITION', BIGINT(unsigned=True), nullable=True)
    proximal_mapping = db.Column('PROXIMAL_MAPPING', db.String(50), nullable=True)
    proximal_percent_identity = db.Column('PROXIMAL_PERCENT_IDENTITY', db.String(50), nullable=True)
    proximal_sequence = db.Column('PROXIMAL_SEQUENCE', db.Text, nullable=True)
    junction_sequence = db.Column('JUNCTION_SEQUENCE', db.Text, nullable=True)
    distal_sequence = db.Column('DISTAL_SEQUENCE', db.Text, nullable=True)
    proximal_sequence_length = db.Column('PROXIMAL_SEQUENCE_LENGTH', BIGINT(unsigned=True), nullable=True)
    distal_mapping = db.Column('DISTAL_MAPPING', db.Text, nullable=True)
    distal_percent_identity = db.Column('DISTAL_PERCENT_IDENTITY', db.String(50), nullable=True)
    distal_sequence_length = db.Column('DISTAL_SEQUENCE_LENGTH', BIGINT(unsigned=True), nullable=True)
    element = db.Column('ELEMENT', db.String(50), nullable=True)
    unique_reads = db.Column('UNIQUE_READS', BIGINT(unsigned=True), nullable=True)
    supporting_reads = db.Column('SUPPORTING_READS', BIGINT(unsigned=True), nullable=True)
    endogenous = db.Column('ENDOGENOUS', db.Boolean, default=False,
                           nullable=False)
    source = db.Column('SOURCE', db.String(50), nullable=True)
    duplicates = db.Column('DUPLICATES', db.String(50), nullable=True)

    duplicates_dict = {}
    proximal_percent = None
    distal_percent = None
    masked = None
    masked_by = None
    comment = None

    def __init__(self, end, position, proximal_mapping,
                 proximal_percent_identity, proximal_sequence,
                 junction_sequence, proximal_sequence_length, distal_sequence,
                 distal_mapping, distal_percent_identity,
                 distal_sequence_length, element, unique_reads,
                 supporting_reads, endogenous, source, duplicates):
        self.end = end
        self.position = position
        self.proximal_mapping = proximal_mapping
        self.proximal_percent_identity = proximal_percent_identity
        self.proximal_sequence = proximal_sequence
        self.junction_sequence = junction_sequence
        self.distal_sequence = distal_sequence
        self.proximal_sequence_length = proximal_sequence_length
        self.distal_mapping = distal_mapping
        self.distal_percent_identity = distal_percent_identity
        self.distal_sequence_length = distal_sequence_length
        self.element = element
        self.unique_reads = unique_reads
        self.supporting_reads = supporting_reads
        self.endogenous = endogenous
        self.source = source
        self.duplicates = duplicates

    def __repr__(self):
        return (
            "<id {}, proximal_mapping {}, percent_identity {}, proximal{}, sequence{}, length{}, distal_mapping{},"
            " distal_percent_identity{}, distal_sequence_length{}, element{}, unique_reads{}, supporting_reads{}"
            ">").format(
            self.id,
            self.proximal_mapping,
            self.proximal_percent_identity,
            self.proximal_sequence,
            self.junction_sequence,
            self.proximal_sequence_length,
            self.distal_mapping,
            self.distal_percent_identity,
            self.distal_sequence_length,
            self.element,
            self.unique_reads,
            self.supporting_reads,
        )

    def as_dict(self):
        return {
            "id": self.id,
            "end": self.end,
            "position": self.position,
            "proximal_mapping": self.proximal_mapping,
            "proximal_percent_identity": self.proximal_percent_identity,
            "proximal_sequence": self.proximal_sequence,
            "junction_sequence": self.junction_sequence,
            "distal_sequence": self.distal_sequence,
            "proximal_sequence_length": self.proximal_sequence_length,
            "distal_mapping": self.distal_mapping,
            "distal_percent_identity": self.distal_percent_identity,
            "distal_sequence_length": self.distal_sequence_length,
            "element": self.element,
            "unique_reads": self.unique_reads,
            "masked": 'True' if self.masked else 'False',
            "supporting_reads": self.supporting_reads,
            "endogenous": 'True' if self.endogenous else 'False',
            "source": self.source,
            "duplicates": self.duplicates
        }

    def convert_proximal_mapping(self):
        prox_map_str = ""
        if self.proximal_mapping:
            prox_map_arr = self.proximal_mapping.split(",")
            if len(prox_map_arr) == 4:
                construct_id, map_start_loc, map_end_loc, percent = prox_map_arr
                self.proximal_percent = percent
                prox_map_str = construct_id + ":" + map_start_loc + "-" + map_end_loc

        return prox_map_str

    def convert_distal_mapping(self):
        distal_map_str = ""
        if self.distal_mapping and self.distal_sequence_length:
            distal_map_arr = self.distal_mapping.split(",")
            if len(distal_map_arr) == 4:
                chromosome, map_start_loc, map_end_loc, percent = distal_map_arr
                self.distal_percent = percent
                distal_map_str = "Distal:1-" + str(self.distal_sequence_length) + "=>" \
                                 + chromosome + ":" + map_start_loc + "-" + map_end_loc + " " + percent

        return distal_map_str

    def browse_junction_as_dict(self):
        return {
            "id": self.id,
            "end": self.end,
            "position": self.position,
            "proximal_mapping": self.convert_proximal_mapping(),
            "proximal_percent_identity": self.proximal_percent_identity,
            "proximal_sequence_length": self.proximal_sequence_length,
            "distal_mapping_percent_identity": self.convert_distal_mapping(),
            "proximal_percent": self.proximal_percent,
            "distal_percent:": self.distal_percent,
            "distal_percent_identity": self.distal_percent_identity,
            "distal_sequence": self.distal_sequence,
            "distal_sequence_length": self.distal_sequence_length,
            "element": self.element,
            "unique_reads": self.unique_reads,
            "supporting_reads": self.supporting_reads,
            "masked": self.masked,
            "masked_by": self.masked_by,
            "comment": self.comment,
            "duplicates_dict": self.duplicates_dict,
            "junction_sequence": self.junction_sequence,
            "source": self.source
        }
