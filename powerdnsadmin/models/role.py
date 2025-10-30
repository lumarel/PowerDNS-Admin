from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db


class Role(db.Model):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(64), index=True, unique=True)
    description: Mapped[str] = mapped_column(db.String(128))

    # Relationships
    users: Mapped[List["User"]] = relationship('User', back_populates='role')
    apikeys: Mapped[List["ApiKey"]] = relationship('ApiKey', back_populates='role')

    def __init__(self, id=None, name=None, description=None):
        self.id = id
        self.name = name
        self.description = description

    # allow database autoincrement to do its own ID assignments
    def __init__(self, name=None, description=None):
        self.id = None
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Role {0}>'.format(self.name)
