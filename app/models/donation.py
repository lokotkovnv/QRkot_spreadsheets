from sqlalchemy import Column, ForeignKey, Integer, Text

from app.models.base import AbstractBaseModel


class Donation(AbstractBaseModel):
    comment = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))
