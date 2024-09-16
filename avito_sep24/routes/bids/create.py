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
from avito_sep24.schemas.bid import BidAuthorType, BidCreateModel, BidFeedback, BidModel
from avito_sep24.schemas.tender import TenderStatus

router = APIRouter()


@router.post("/api/bids/new")
def create_new_bid(
    model: BidCreateModel,
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repository)],
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
) -> BidModel:
    try:
        tender_id = uuid.UUID(model.tender_id)
    except ValueError as e:
        raise ClientRequestError(404, "tender id invalid") from e

    tender = tender_repo.find_by_id(tender_id)
    assert404(tender is not None, "tender not found")

    assert403(tender.status == TenderStatus.PUBLISHED, "you can't bid to this tender")

    try:
        author_id = uuid.UUID(model.author_id)
    except ValueError as e:
        raise ClientRequestError(401, "author id invalid") from e

    if model.author_type == BidAuthorType.USER:
        author = employee_repo.find_by_id(author_id)
        assert401(author is not None, "no such employee")
    else:
        author = org_repo.find_by_id(author_id)
        assert401(author is not None, "no such organization")

    bid_version = bid_repo.create_as_version(
        name=model.name,
        description=model.description,
        tender_id=tender_id,
        author_type=model.author_type,
        author_id=author_id,
    )
    return bid_version.as_model()


@router.put("/api/bids/{bid_id}/feedback")
def create_bid_review(
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repository)],
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    bid_id: str,
    bidFeedback: BidFeedback,  # noqa
    username: str,
) -> BidModel:
    employee = employee_repo.find_by_username(username)
    assert401(employee is not None, "no employee found with such username")

    try:
        bid_uuid = uuid.UUID(bid_id)
    except ValueError as e:
        raise ClientRequestError(404, "invalid bid_id") from e

    bid = bid_repo.find_by_id(bid_uuid)
    assert404(bid is not None, "no such bid found")

    has_access = tender_repo.has_write_access(
        bid.tender.id,
        employee.id,
        org_repo,
    )
    assert403(has_access)

    bid_repo.create_review(
        employee_id=employee.id,
        bid_id=bid.id,
        description=bidFeedback,
    )
    return bid_repo.get_last_version_by_id(bid.id).as_model()
