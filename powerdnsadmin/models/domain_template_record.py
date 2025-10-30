from typing import Optional
from flask import current_app
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db


class DomainTemplateRecord(db.Model):
    __tablename__ = "domain_template_record"
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)
    type: Mapped[Optional[str]] = mapped_column(db.String(64), nullable=True)
    ttl: Mapped[Optional[int]] = mapped_column(db.Integer, nullable=True)
    data: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(db.Text, nullable=True)
    status: Mapped[Optional[bool]] = mapped_column(db.Boolean, nullable=True)
    template_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('domain_template.id'))

    # Relationships
    template: Mapped["DomainTemplate"] = relationship('DomainTemplate', back_populates='records')

    def __repr__(self):
        return '<DomainTemplateRecord {0}>'.format(self.id)

    def __init__(self,
                 id=None,
                 name=None,
                 type=None,
                 ttl=None,
                 data=None,
                 comment=None,
                 status=None):
        self.id = id
        self.name = name
        self.type = type
        self.ttl = ttl
        self.data = data
        self.comment = comment
        self.status = status

    def apply(self):
        try:
            db.session.commit()
        except Exception as e:
            current_app.logger.error(
                'Can not update zone template table. Error: {0}'.format(e))
            db.session.rollback()
            return {
                'status': 'error',
                'msg': 'Can not update zone template table'
            }
