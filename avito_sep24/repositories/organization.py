from collections.abc import Iterator
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import exists
from sqlalchemy.orm import Session

from avito_sep24.database import get_session
from avito_sep24.models import Organization, OrganizationResponsible


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, organization_id: UUID) -> Organization | None:
        return self.session.get(Organization, organization_id)

    def is_responsible(self, organization_id: UUID, employee_id: UUID) -> bool:
        stmt = self.session.query(
            exists().where(
                OrganizationResponsible.organization_id == organization_id,
                OrganizationResponsible.user_id == employee_id,
            )
        )
        return self.session.scalar(stmt)


def get_org_repository(
    session: Annotated[Session, Depends(get_session)],
) -> Iterator[OrganizationRepository]:
    yield OrganizationRepository(session)
