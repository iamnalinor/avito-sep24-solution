import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from avito_sep24.errors import ClientRequestError, assert401, assert403, assert404
from avito_sep24.repositories.bid import BidRepository, get_bid_repository
from avito_sep24.repositories.employee import (
    EmployeeRepository,
    get_employee_repository,
)
from avito_sep24.repositories.organization import (
    OrganizationRepository,
    get_org_repository,
)
from avito_sep24.repositories.tender import TenderRepository, get_tender_repository
from avito_sep24.schemas.bid import BidModel, BidStatus
from avito_sep24.schemas.pagination import PaginationLimit, PaginationOffset

router = APIRouter()


@router.get("/api/bids/{tender_id}/list")
def get_bids_for_tender(
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repository)],
    tender_id: str,
    username: str,
    limit: PaginationLimit = 5,
    offset: PaginationOffset = 0,
) -> list[BidModel]:
    employee = employee_repo.find_by_username(username)
    assert401(employee is not None, "no employee found with such username")

    try:
        tender_uuid = uuid.UUID(tender_id)
    except ValueError as e:
        raise ClientRequestError(404, "invalid tender_id") from e

    tender = tender_repo.find_by_id(tender_uuid)
    assert404(tender is not None, "no such tender found")

    have_access = tender_repo.has_write_access(
        tender.id,
        employee.id,
        org_repo,
    )
    assert403(have_access)

    return [
        bid_version.as_model()
        for bid_version in bid_repo.get_published_paginated(
            tender.id,
            limit,
            offset,
        )
    ]


@router.get("/api/bids/my")
def get_my_tenders(
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    username: str | None = None,
    limit: PaginationLimit = 5,
    offset: PaginationOffset = 0,
) -> list[BidModel]:
    if username is None:
        return []

    employee = employee_repo.find_by_username(username)
    assert401(employee is not None, "no employee found with such username")

    return [
        bid_version.as_model()
        for bid_version in bid_repo.get_created_by_employee(
            employee.id,
            limit,
            offset,
        )
    ]


@router.get("/api/bids/{bid_id}/status")
def get_bid_status(
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repository)],
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
    bid_id: str,
    username: str,
) -> BidStatus:
    employee = employee_repo.find_by_username(username)
    assert401(employee is not None, "no employee found with such username")
    employee_id = employee.id

    try:
        bid_uuid = uuid.UUID(bid_id)
    except ValueError as e:
        raise ClientRequestError(404, "invalid bid_id") from e

    bid = bid_repo.find_by_id(bid_uuid)
    assert404(bid is not None, "no such bid found")

    has_access = bid_repo.has_read_access(
        bid.id,
        employee_id,
        org_repo,
    )
    assert403(has_access)

    return bid.status
