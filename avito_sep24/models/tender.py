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
from avito_sep24.schemas.tender import TenderModel, TenderServiceType, TenderStatus


class Tender(Base):
    __tablename__ = "tender"

    status = mapped_column(
        Enum(TenderStatus), nullable=False, default=TenderStatus.CREATED
    )
    organization_id = mapped_column(Uuid, ForeignKey("organization.id"), nullable=False)
    creator_id = mapped_column(Uuid, ForeignKey("employee.id"), nullable=False)


class TenderVersion(Base):
    __tablename__ = "tender_version"

    tender_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("tender.id"), nullable=False
    )
    tender: Mapped[Tender] = relationship(Tender)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    service_type: Mapped[TenderServiceType] = mapped_column(
        Enum(TenderServiceType), nullable=False
    )
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    actual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint("tender_id", "index", name="unique_tender_version_index"),
    )

    def as_model(self) -> TenderModel:
        return TenderModel(
            id=self.tender_id,
            name=self.name,
            description=self.description,
            service_type=self.service_type,
            status=self.tender.status,
            version=self.index,
            created_at=self.tender.created_at,
            organization_id=self.tender.organization_id,
        )
