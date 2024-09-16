from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column

from avito_sep24.database import Base, RawBase


class Organization(Base):
    __tablename__ = "organization"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(100), nullable=False)


class OrganizationResponsible(RawBase):
    __tablename__ = "organization_responsible"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    organization_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("organization.id", ondelete="CASCADE")
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("employee.id", ondelete="CASCADE")
    )
