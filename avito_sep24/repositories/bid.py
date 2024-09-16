from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from avito_sep24.database import get_session
from avito_sep24.models import Bid, BidReview, BidVersion
from avito_sep24.repositories.organization import OrganizationRepository
from avito_sep24.schemas.bid import BidAuthorType, BidStatus


class BidRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_as_version(
        self,
        name: str,
        description: str,
        tender_id: UUID,
        author_type: BidAuthorType,
        author_id: UUID,
    ) -> BidVersion:
        bid = Bid(
            tender_id=tender_id,
            author_type=author_type,
            author_id=author_id,
        )
        bid_version = BidVersion(
            bid=bid,
            name=name,
            description=description,
            index=1,
        )

        self.session.add(bid)
        self.session.add(bid_version)
        self.session.commit()

        return bid_version

    def find_by_id(self, bid_id: UUID) -> Bid | None:
        return self.session.get(Bid, bid_id)

    def get_version_by_id(self, bid_id: UUID, index: int) -> BidVersion:
        stmt = select(BidVersion).filter(
            BidVersion.bid_id == bid_id,
            BidVersion.index == index,
        )
        version = self.session.scalar(stmt)
        if version is None:
            raise NoResultFound
        return version

    def get_last_version_by_id(self, bid_id: UUID) -> BidVersion:
        stmt = select(BidVersion).filter(BidVersion.bid_id == bid_id, BidVersion.actual)
        version = self.session.scalar(stmt)
        if version is None:
            raise NoResultFound
        return version

    def get_published_paginated(
        self,
        tender_id: UUID,
        limit: int = 5,
        offset: int = 0,
    ) -> list[BidVersion]:
        stmt = select(BidVersion).filter(
            BidVersion.bid.has(status=BidStatus.PUBLISHED),
            BidVersion.bid.has(tender_id=tender_id),
        )
        stmt = stmt.offset(offset).limit(limit)
        return list(self.session.scalars(stmt))

    def get_created_by_employee(
        self,
        employee_id: UUID,
        limit: int = 5,
        offset: int = 0,
    ) -> list[BidVersion]:
        stmt = (
            select(BidVersion)
            .filter(
                BidVersion.bid.has(
                    author_id=employee_id, author_type=BidAuthorType.USER
                )
            )
            .offset(offset)
            .limit(limit)
        )
        return list(self.session.scalars(stmt))

    def has_read_access(
        self, bid_id: UUID, employee_id: UUID, org_repo: OrganizationRepository
    ) -> bool:
        bid = self.find_by_id(bid_id)
        if bid is None:
            raise NoResultFound

        if self.has_write_access(bid_id, employee_id, org_repo):
            return True

        if bid.status == BidStatus.PUBLISHED:
            return org_repo.is_responsible(bid.tender.organization_id, employee_id)

        return False

    def has_write_access(
        self, bid_id: UUID, employee_id: UUID, org_repo: OrganizationRepository
    ) -> bool:
        bid = self.find_by_id(bid_id)
        if bid is None:
            raise NoResultFound

        if bid.author_type == BidAuthorType.USER:
            return bid.author_id == employee_id

        return org_repo.is_responsible(bid.author_id, employee_id)

    def update_status(self, bid_id: UUID, status: BidStatus) -> None:
        stmt = update(Bid).where(Bid.id == bid_id).values(status=status)
        self.session.execute(stmt)
        self.session.commit()

    def update(
        self,
        bid_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> BidVersion:
        old_version = self.get_last_version_by_id(bid_id)
        stmt = (
            update(BidVersion)
            .where(BidVersion.id == old_version.id)
            .values(actual=False)
        )
        self.session.execute(stmt)

        new_version = BidVersion(
            bid_id=bid_id,
            index=old_version.index + 1,
            name=name or old_version.name,
            description=description or old_version.description,
        )
        self.session.add(new_version)

        self.session.commit()

        return new_version

    def create_review(
        self, employee_id: UUID, bid_id: UUID, description: str
    ) -> BidReview:
        bid_review = BidReview(
            bid_id=bid_id,
            author_id=employee_id,
            description=description,
        )
        self.session.add(bid_review)
        self.session.commit()
        return bid_review


def get_bid_repository(
    session: Annotated[Session, Depends(get_session)],
) -> Iterator[BidRepository]:
    yield BidRepository(session)
