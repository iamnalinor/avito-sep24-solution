from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from avito_sep24.database import get_session
from avito_sep24.models import Tender, TenderVersion
from avito_sep24.repositories.organization import OrganizationRepository
from avito_sep24.schemas.tender import TenderServiceType, TenderStatus


class TenderRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_as_version(
        self,
        name: str,
        description: str,
        service_type: TenderServiceType,
        organization_id: UUID,
        creator_id: UUID,
    ) -> TenderVersion:
        tender = Tender(
            organization_id=organization_id,
            creator_id=creator_id,
        )
        tender_version = TenderVersion(
            tender=tender,
            name=name,
            description=description,
            service_type=service_type,
            index=1,
        )

        self.session.add(tender)
        self.session.add(tender_version)
        self.session.commit()

        return tender_version

    def find_by_id(self, tender_id: UUID) -> Tender | None:
        return self.session.get(Tender, tender_id)

    def get_version_by_id(self, tender_id: UUID, index: int) -> TenderVersion:
        stmt = select(TenderVersion).filter(
            TenderVersion.tender_id == tender_id, TenderVersion.index == index
        )
        version = self.session.scalar(stmt)
        if version is None:
            raise NoResultFound
        return version

    def get_last_version_by_id(self, tender_id: UUID) -> TenderVersion:
        stmt = select(TenderVersion).filter(
            TenderVersion.tender_id == tender_id, TenderVersion.actual
        )
        version = self.session.scalar(stmt)
        if version is None:
            raise NoResultFound
        return version

    def get_public_paginated(
        self,
        limit: int = 5,
        offset: int = 0,
        service_types: list[TenderServiceType] | None = None,
    ) -> list[TenderVersion]:
        stmt = select(TenderVersion).filter(
            TenderVersion.tender.has(status=TenderStatus.PUBLISHED)
        )
        if service_types is not None:
            stmt = stmt.filter(TenderVersion.service_type.in_(service_types))
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.scalars(stmt))

    def get_created_by_employee(
        self,
        employee_id: UUID,
        limit: int = 5,
        offset: int = 0,
    ) -> list[TenderVersion]:
        stmt = (
            select(TenderVersion)
            .filter(TenderVersion.tender.has(creator_id=employee_id))
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def has_read_access(
        self, tender_id: UUID, employee_id: UUID, org_repo: OrganizationRepository
    ) -> bool:
        tender = self.find_by_id(tender_id)
        if tender is None:
            raise NoResultFound

        if tender.status == TenderStatus.PUBLISHED:
            return True

        return org_repo.is_responsible(tender.organization_id, employee_id)

    def has_write_access(
        self, tender_id: UUID, employee_id: UUID, org_repo: OrganizationRepository
    ) -> bool:
        tender = self.find_by_id(tender_id)
        if tender is None:
            raise NoResultFound

        return org_repo.is_responsible(tender.organization_id, employee_id)

    def update_status(self, tender_id: UUID, status: TenderStatus) -> None:
        stmt = update(Tender).where(Tender.id == tender_id).values(status=status)
        self.session.execute(stmt)
        self.session.commit()

    def update(
        self,
        tender_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        service_type: TenderServiceType | None = None,
    ) -> TenderVersion:
        old_version = self.get_last_version_by_id(tender_id)
        stmt = (
            update(TenderVersion)
            .where(TenderVersion.id == old_version.id)
            .values(actual=False)
        )
        self.session.execute(stmt)

        new_version = TenderVersion(
            tender_id=tender_id,
            index=old_version.index + 1,
            name=name or old_version.name,
            description=description or old_version.description,
            service_type=service_type or old_version.service_type,
        )
        self.session.add(new_version)

        self.session.commit()

        return new_version


def get_tender_repository(
    session: Annotated[Session, Depends(get_session)],
) -> Iterator[TenderRepository]:
    yield TenderRepository(session)
