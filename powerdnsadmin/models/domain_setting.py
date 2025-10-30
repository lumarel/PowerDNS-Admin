import traceback
from typing import Optional
from flask import current_app
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import db


class DomainSetting(db.Model):
    __tablename__ = 'domain_setting'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    domain_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey('domain.id'))
    setting: Mapped[str] = mapped_column(db.String(255), nullable=False)
    value: Mapped[Optional[str]] = mapped_column(db.String(255), nullable=True)

    # Relationships
    domain: Mapped["Domain"] = relationship('Domain', back_populates='settings')


    def __init__(self, id=None, setting=None, value=None):
        self.id = id
        self.setting = setting
        self.value = value

    def __repr__(self):
        return '<DomainSetting {0} for {1}>'.format(setting, self.domain.name)

    def __eq__(self, other):
        return type(self) == type(other) and self.setting == other.setting

    def set(self, value):
        try:
            self.value = value
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(
                'Unable to set DomainSetting value. DETAIL: {0}'.format(e))
            current_app.logger.debug(traceback.format_exc())
            db.session.rollback()
            return False
