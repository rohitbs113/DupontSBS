from sqlalchemy.ext.declarative import declared_attr

from sbs.database_utility import db


class BaseModel(db.Model):
    __abstract__ = True

    created_on = db.Column('CREATED_ON', db.TIMESTAMP, default=db.func.now(), nullable=False)
    updated_on = db.Column('UPDATED_ON', db.TIMESTAMP, default=db.func.now(), onupdate=db.func.now(), nullable=False)

    @declared_attr
    def created_by(cls):
        return db.Column('CREATED_BY', db.String(50), db.ForeignKey('USER_ROLE.USERNAME'), default='system',
                         nullable=False)

    @declared_attr
    def updated_by(cls):
        return db.Column('UPDATED_BY', db.String(50), db.ForeignKey('USER_ROLE.USERNAME'), default='system',
                         nullable=False)
