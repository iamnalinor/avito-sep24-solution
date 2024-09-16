import datetime
import enum
import uuid
from typing import Annotated

from pydantic import Field, StringConstraints

from avito_sep24.schemas import BaseSchema

__all__ = [
    "BidName",
    "BidDescription",
    "BidFeedback",
    "BidDecisionType",
    "BidAuthorType",
    "BidModel",
    "BidStatus",
    "BidUpdateModel",
    "BidVersionField",
    "BidCreateModel",
]

BidName = Annotated[str, StringConstraints(max_length=100)]
BidDescription = Annotated[str, StringConstraints(max_length=500)]
BidFeedback = Annotated[str, StringConstraints(max_length=1000)]
BidVersionField = Annotated[int, Field(ge=1)]


class BidDecisionType(enum.Enum):
    APPROVED = "Approved"
    REJECTED = "Rejected"


class BidAuthorType(enum.Enum):
    ORGANIZATION = "Organization"
    USER = "User"


class BidStatus(enum.Enum):
    CREATED = "Created"
    PUBLISHED = "Published"
    CLOSED = "Closed"


class _BidBaseModel(BaseSchema):
    name: BidName
    description: BidDescription
    author_type: BidAuthorType


class BidCreateModel(_BidBaseModel):
    tender_id: str
    author_id: str


class BidUpdateModel(BaseSchema):
    name: BidName | None = None
    description: BidDescription | None = None


class BidModel(_BidBaseModel):
    id: uuid.UUID
    created_at: datetime.datetime
    status: BidStatus
    tender_id: uuid.UUID
    author_id: uuid.UUID
    version: BidVersionField
