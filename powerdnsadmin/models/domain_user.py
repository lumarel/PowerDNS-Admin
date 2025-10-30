from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import db


class DomainUser(db.Model):
    __tablename__ = 'domain_user'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    domain_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey('domain.id'),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    def __init__(self, domain_id, user_id):
        self.domain_id = domain_id
        self.user_id = user_id

    def __repr__(self):
        return '<Domain_User {0} {1}>'.format(self.domain_id, self.user_id)
