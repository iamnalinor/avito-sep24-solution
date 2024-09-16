from uuid import UUID

from sqlalchemy import ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from avito_sep24.database import Base


class BidReview(Base):
    __tablename__ = "bid_review"

    bid_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("bid.id"), nullable=False)
    author_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("employee.id"), nullable=False
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
