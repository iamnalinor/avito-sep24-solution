import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from avito_sep24.utils import format_datetime


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        json_encoders={
            datetime.datetime: format_datetime,
        },
    )
