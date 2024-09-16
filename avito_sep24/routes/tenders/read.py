import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from avito_sep24.errors import ClientRequestError, assert401, assert403, assert404
from avito_sep24.repositories.employee import (
    EmployeeRepository,
    get_employee_repository,
)
from avito_sep24.repositories.organization import (
    OrganizationRepository,
    get_org_repository,
)
from avito_sep24.repositories.tender import TenderRepository, get_tender_repository
from avito_sep24.schemas.pagination import PaginationLimit, PaginationOffset
from avito_sep24.schemas.tender import (
    TenderModel,
    TenderServiceType,
    TenderStatus,
)

router = APIRouter()


@router.get("/api/tenders")
def get_tenders(
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    service_type: Annotated[list[TenderServiceType] | None, Query()] = None,
    limit: PaginationLimit = 5,
    offset: PaginationOffset = 0,
) -> list[TenderModel]:
    return [
        tender_version.as_model()
        for tender_version in tender_repo.get_public_paginated(
            limit, offset, service_type
        )
    ]


@router.get("/api/tenders/my")
def get_my_tenders(
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    username: str | None = None,
    limit: PaginationLimit = 5,
    offset: PaginationOffset = 0,
) -> list[TenderModel]:
    if username is None:
        return []

    employee = employee_repo.find_by_username(username)
    assert401(employee is not None, "no employee found with such username")

    return [
        tender_version.as_model()
        for tender_version in tender_repo.get_created_by_employee(
            employee.id,
            limit,
            offset,
        )
    ]


@router.get("/api/tenders/{tender_id}/status")
def get_tender_status(
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repository)],
    tender_id: str,
    username: str | None = None,
) -> TenderStatus:
    if username is not None:
        employee = employee_repo.find_by_username(username)
        assert401(employee is not None, "no employee found with such username")
        employee_id = employee.id
    else:
        employee_id = uuid.uuid4()  # random UUID for anonymous user

    try:
        tender_uuid = uuid.UUID(tender_id)
    except ValueError as e:
        raise ClientRequestError(404, "invalid tender_id") from e

    tender = tender_repo.find_by_id(tender_uuid)
    assert404(tender is not None, "no such tender found")

    has_access = tender_repo.has_read_access(
        tender.id,
        employee_id,
        org_repo,
    )
    assert403(has_access)

    return tender.status
