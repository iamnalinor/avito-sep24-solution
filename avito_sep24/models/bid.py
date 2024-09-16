from uuid import UUID

from sqlalchemy import (
    Boolean,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from avito_sep24.database import Base
from avito_sep24.schemas.bid import BidAuthorType, BidDecisionType, BidModel, BidStatus

from .employee import Employee
from .tender import Tender


class Bid(Base):
    __tablename__ = "bid"

    status: Mapped[BidStatus] = mapped_column(
        Enum(BidStatus), nullable=False, default=BidStatus.CREATED
    )
    tender_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tender.id"), nullable=False
    )
    tender: Mapped[Tender] = relationship(Tender)
    author_type: Mapped[BidAuthorType] = mapped_column(
        Enum(BidAuthorType), nullable=False
    )
    author_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)


class BidVersion(Base):
    __tablename__ = "bid_version"

    bid_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("bid.id"), nullable=False)
    bid: Mapped[Bid] = relationship(Bid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    actual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("bid_id", "index", name="unique_bid_version_index"),
    )

    def as_model(self) -> BidModel:
        return BidModel(
            id=self.bid_id,
            name=self.name,
            description=self.description,
            tender_id=self.bid.tender_id,
            author_type=self.bid.author_type,
            author_id=self.bid.author_id,
            version=self.index,
            created_at=self.bid.created_at,
            status=self.bid.status,
        )


class BidDecision(Base):
    __tablename__ = "bid_decision"

    bid_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("bid.id"), nullable=False)
    bid: Mapped[Bid] = relationship(Bid)
    author_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("employee.id"), nullable=False
    )
    author: Mapped[Employee] = relationship(Employee)
    decision: Mapped[BidDecisionType] = mapped_column(
        Enum(BidDecisionType), nullable=False
    )

    __table_args__ = (
        UniqueConstraint("bid_id", "author_id", name="unique_bid_decision_index"),
    )
