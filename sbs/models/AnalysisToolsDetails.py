from sqlalchemy.dialects.mysql import INTEGER

from sbs.models.BaseModel import BaseModel
from sbs.database_utility import db


class AnalysisToolsDetails(BaseModel):
    __tablename__ = 'ANALYSIS_TOOLS_DETAILS'
    id = db.Column('ID', INTEGER(unsigned=True), primary_key=True, unique=True)
    pipeline_call = db.Column('PIPELINE_CALL', db.String(20), nullable=True)
    current_call = db.Column('CURRENT_CALL', db.String(20), nullable=True)
    pipeline_msg = db.Column('PIPELINE_MSG', db.String(500), nullable=True)
    current_msg = db.Column('CURRENT_MSG', db.String(500), nullable=True)
    current_detail = db.Column('CURRENT_DETAIL', db.Text, nullable=True)

    analysis_id = db.Column('ANALYSIS_ID', INTEGER(unsigned=True),
                            db.ForeignKey('ANALYSIS.ID'))
    tool_id = db.Column('TOOL_ID', INTEGER(unsigned=True),
                       db.ForeignKey('ANALYSIS_TOOLS.ID'))

    pipeline_detail = None
    custom_pipeline_detail = None

    def __init__(self, pipeline_call, current_call, pipeline_msg, current_msg,
                 current_detail, analysis_id, tool_id):
        self.pipeline_call = pipeline_call
        self.current_call = current_call
        self.pipeline_msg = pipeline_msg
        self.current_msg = current_msg
        self.current_detail = current_detail
        self.analysis_id = analysis_id
        self.tool_id = tool_id

    def __repr__(self):
        return (
            "<id {}, tool {}, pipeline_call {}>").format(
            self.id,
            self.tool_id,
            self.pipeline_call
        )

    def as_dict(self):
        return {
            "id": self.id,
            "pipeline_call": self.pipeline_call,
            "current_call": self.current_call,
            "pipeline_msg": self.pipeline_msg,
            "current_msg": self.current_msg,
            "pipeline_detail": self.pipeline_detail, 
            "current_detail": self.current_detail,
            "custom_pipeline_detail": self.custom_pipeline_detail,
            "analysis_id": self.analysis_id,
            "tool_id": self.tool_id
        }
