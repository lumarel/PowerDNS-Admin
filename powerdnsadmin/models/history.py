import traceback
from typing import Optional
from flask import current_app
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import db


class History(db.Model):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    # format of msg field must not change. History traversing is done using part of the msg field
    msg: Mapped[str] = mapped_column(db.String(256))
    # detail = db.Column(db.Text().with_variant(db.Text(length=2**24-2), 'mysql'))
    detail: Mapped[str] = mapped_column(db.Text())
    created_by: Mapped[str] = mapped_column(db.String(128))
    created_on: Mapped[datetime] = mapped_column(
        db.DateTime, 
        index=True, 
        default=datetime.now(timezone.utc)
    )
    domain_id: Mapped[Optional[int]] = mapped_column(
        db.Integer,
        db.ForeignKey('domain.id'),
        nullable=True
    )
    
    def __init__(self, id=None, msg=None, detail=None, created_by=None, domain_id=None):
        self.id = id
        self.msg = msg
        self.detail = detail
        self.created_by = created_by
        self.domain_id = domain_id

    def __repr__(self):
        return '<History {0}>'.format(self.msg)

    def add(self):
        """
        Add an event to history table
        """
        h = History()
        h.msg = self.msg
        h.detail = self.detail
        h.created_by = self.created_by
        h.domain_id = self.domain_id
        db.session.add(h)
        db.session.commit()

    def remove_all(self):
        """
        Remove all history from DB
        """
        try:
            db.session.query(History).delete()
            db.session.commit()
            current_app.logger.info("Removed all history")
            return True
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("Cannot remove history. DETAIL: {0}".format(e))
            current_app.logger.debug(traceback.format_exc())
            return False
