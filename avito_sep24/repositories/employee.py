import uuid
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from avito_sep24.database import get_session
from avito_sep24.models import Employee


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_by_id(self, employee_id: uuid.UUID) -> Employee | None:
        return self.session.get(Employee, employee_id)

    def find_by_username(self, username: str) -> Employee | None:
        stmt = select(Employee).where(Employee.username == username)
        return self.session.scalar(stmt)


def get_employee_repository(
    session: Annotated[Session, Depends(get_session)],
) -> Iterator[EmployeeRepository]:
    yield EmployeeRepository(session)
