from sbs.database_utility import db
from sbs.models.BaseModel import BaseModel
import enum


class UserRole(enum.Enum):
    lab = "lab"
    client = "client"

class UserRole(BaseModel):
    __tablename__ = 'USER_ROLE'
    user_name = db.Column('USERNAME', db.String(50), primary_key=True, unique=True)
    role = db.Column('ROLE', db.Enum(UserRole), nullable=False)
    active = db.Column('ACTIVE', db.Boolean, default=True, nullable=False)

    def __init__(self, user_name, role, active):
        self.user_name = user_name
        self.role = role
        self.active = active

    def __repr__(self):
        return ("<UserName {},Role {}, Active {}," +
                "CreatedOn {}, UpdatedOn {}, CreatedBy {}, " +
                "UpdatedBy {}>").format(self.user_name, self.role,
                                        self.active, self.created_on,
                                        self.updated_on, self.created_by,
                                        self.updated_by)

    def as_dict(self):
        return {
            'user_name': self.user_name,
            'role': self.role.value,
            'active': self.active
        }
