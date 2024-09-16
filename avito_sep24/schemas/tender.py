import datetime
import enum
import uuid
from typing import Annotated

from pydantic import Field, StringConstraints

from avito_sep24.schemas import BaseSchema

__all__ = [
    "TenderModel",
    "TenderCreateModel",
    "TenderUpdateModel",
    "TenderName",
    "TenderDescription",
    "TenderVersionField",
    "TenderServiceType",
    "TenderStatus",
]


TenderName = Annotated[str, StringConstraints(max_length=100)]
TenderDescription = Annotated[str, StringConstraints(max_length=500)]
TenderVersionField = Annotated[int, Field(ge=1)]


class TenderServiceType(enum.Enum):
    CONSTRUCTION = "Construction"
    DELIVERY = "Delivery"
    MANUFACTURE = "Manufacture"


class TenderStatus(enum.Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CLOSED = "Closed"


class _TenderBaseModel(BaseSchema):
    name: TenderName
    description: TenderDescription
    service_type: TenderServiceType


class TenderCreateModel(_TenderBaseModel):
    creator_username: str
    organization_id: str


class TenderUpdateModel(BaseSchema):
    name: TenderName | None = None
    description: TenderDescription | None = None
    service_type: TenderServiceType | None = None


class TenderModel(_TenderBaseModel):
    id: uuid.UUID
    status: TenderStatus
    version: TenderVersionField
    created_at: datetime.datetime
    organization_id: uuid.UUID
