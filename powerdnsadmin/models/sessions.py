import datetime
from flask import current_app, session
from flask_login import current_user
from typing import Optional
from .base import db
from sqlalchemy.orm import Mapped, mapped_column

class Sessions(db.Model):
    __tablename__ = "sessions"
    __table_args__ = {'extend_existing': True}
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    session_id: Mapped[str] = mapped_column(db.String(255), index=True, unique=True)
    data: Mapped[bytes] = mapped_column(db.BLOB)
    expiry: Mapped[datetime] = mapped_column(db.DateTime)

    def __init__(self,
                 id=None,
                 session_id=None,
                 data=None,
                 expiry=None):
        self.id = id
        self.session_id = session_id
        self.data = data
        self.expiry = expiry

    def __repr__(self):
        return '<Sessions {0}>'.format(self.id)

    @staticmethod
    def clean_up_expired_sessions():
        """Clean up expired sessions in the database"""
        from datetime import datetime
        from sqlalchemy import or_
        from sqlalchemy.exc import SQLAlchemyError

        try:
            db.session.query(Sessions).filter(or_(Sessions.expiry < datetime.now(), Sessions.expiry is None)).delete()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(e)
            return False
        return True
