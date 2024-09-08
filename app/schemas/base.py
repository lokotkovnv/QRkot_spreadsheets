from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

CREATE_DATE_EXAMPLE = (
    datetime.now() + timedelta(minutes=10)
).isoformat(timespec='minutes')

CLOSE_DATE_EXAMPLE = (
    datetime.now() + timedelta(hours=1)
).isoformat(timespec='minutes')


class AbstractBaseSchema(BaseModel):
    full_amount: PositiveInt
    invested_amount: int = 0
    fully_invested: bool
    create_date: datetime = Field(..., example=CREATE_DATE_EXAMPLE)
    close_date: Optional[datetime] = Field(None, example=CLOSE_DATE_EXAMPLE)
