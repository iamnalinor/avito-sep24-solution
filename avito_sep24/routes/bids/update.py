import uuid
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from avito_sep24.errors import ClientRequestError, assert401, assert403, assert404
from avito_sep24.models import Bid
from avito_sep24.repositories.bid import BidRepository, get_bid_repository
from avito_sep24.repositories.employee import (
    EmployeeRepository,
    get_employee_repository,
)
from avito_sep24.repositories.organization import (
    OrganizationRepository,
    get_org_repository,
)
from avito_sep24.schemas.bid import (
    BidModel,
    BidStatus,
    BidUpdateModel,
    BidVersionField,
)

router = APIRouter()


def validate_access(
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repository)],
    bid_id: Annotated[str, Path()],
    username: Annotated[str, Query()],
) -> Iterator[Bid]:
    employee = employee_repo.find_by_username(username)
    assert401(employee is not None, "no employee found with such username")

    try:
        bid_uuid = uuid.UUID(bid_id)
    except ValueError as e:
        raise ClientRequestError(404, "invalid bid_id") from e

    bid = bid_repo.find_by_id(bid_uuid)
    assert404(bid is not None, "no such bid found")

    has_access = bid_repo.has_write_access(
        bid.id,
        employee.id,
        org_repo,
    )
    assert403(has_access)

    yield bid


@router.put("/api/bids/{bid_id}/status")
def update_bid_status(
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
    bid: Annotated[Bid, Depends(validate_access)],
    status: BidStatus,
) -> BidModel:
    bid_repo.update_status(bid.id, status)

    return bid_repo.get_last_version_by_id(bid.id).as_model()


@router.patch("/api/bids/{bid_id}/edit")
def update_bid(
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
    bid: Annotated[Bid, Depends(validate_access)],
    update_model: BidUpdateModel,
) -> BidModel:
    new_version = bid_repo.update(
        bid.id,
        **update_model.model_dump(exclude_none=True),
    )

    return new_version.as_model()


@router.put("/api/bids/{bid_id}/rollback/{version}")
def rollback_to_version(
    bid_repo: Annotated[BidRepository, Depends(get_bid_repository)],
    bid: Annotated[Bid, Depends(validate_access)],
    version: BidVersionField,
) -> BidModel:
    old_version = bid_repo.get_version_by_id(bid.id, version)

    return update_bid(
        bid_repo,
        bid,
        BidUpdateModel(
            **{key: getattr(old_version, key) for key in BidUpdateModel.model_fields}
        ),
    )
