from .base import db
from sqlalchemy.orm import Mapped, mapped_column, relationship

class AccountUser(db.Model):
    __tablename__ = 'account_user'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(db.Integer, 
                                          db.ForeignKey('account.id'), 
                                          nullable=False)
    user_id: Mapped[int] = mapped_column(db.Integer, 
                                       db.ForeignKey('user.id'), 
                                       nullable=False)

    def __init__(self, account_id, user_id):
        self.account_id = account_id
        self.user_id = user_id

    def __repr__(self):
        return '<Account_User {0} {1}>'.format(self.account_id, self.user_id)
