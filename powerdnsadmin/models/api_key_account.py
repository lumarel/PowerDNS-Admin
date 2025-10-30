from .base import db
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint

class ApiKeyAccount(db.Model):
    __tablename__ = 'apikey_account'
    
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    apikey_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey('apikey.id'),
        nullable=False
    )
    account_id: Mapped[int] = mapped_column(
        db.Integer,
        db.ForeignKey('account.id'),
        nullable=False
    )
    __table_args__ = (
        UniqueConstraint('apikey_id', 'account_id', name='uniq_apikey_account'),
    )

    def __init__(self, apikey_id, account_id):
        self.apikey_id = apikey_id
        self.account_id = account_id

    def __repr__(self):
        return '<ApiKey_Account {0} {1}>'.format(self.apikey_id, self.account_id)
