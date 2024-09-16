import uuid
from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from avito_sep24.errors import ClientRequestError, assert401, assert403, assert404
from avito_sep24.models import Tender
from avito_sep24.repositories.employee import (
    EmployeeRepository,
    get_employee_repository,
)
from avito_sep24.repositories.organization import (
    OrganizationRepository,
    get_org_repository,
)
from avito_sep24.repositories.tender import TenderRepository, get_tender_repository
from avito_sep24.schemas.tender import (
    TenderModel,
    TenderStatus,
    TenderUpdateModel,
    TenderVersionField,
)

router = APIRouter()


def validate_access(
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repository)],
    tender_id: Annotated[str, Path()],
    username: Annotated[str, Query()],
) -> Iterator[Tender]:
    employee = employee_repo.find_by_username(username)
    assert401(employee is not None, "no employee found with such username")

    try:
        tender_uuid = uuid.UUID(tender_id)
    except ValueError as e:
        raise ClientRequestError(404, "invalid tender_id") from e

    tender = tender_repo.find_by_id(tender_uuid)
    assert404(tender is not None, "no such tender found")

    has_access = tender_repo.has_write_access(
        tender.id,
        employee.id,
        org_repo,
    )
    assert403(has_access)

    yield tender


@router.put("/api/tenders/{tender_id}/status")
def update_tender_status(
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    tender: Annotated[Tender, Depends(validate_access)],
    status: TenderStatus,
) -> TenderModel:
    tender_repo.update_status(tender.id, status)

    return tender_repo.get_last_version_by_id(tender.id).as_model()


@router.patch("/api/tenders/{tender_id}/edit")
def update_tender(
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    tender: Annotated[Tender, Depends(validate_access)],
    update_model: TenderUpdateModel,
) -> TenderModel:
    new_version = tender_repo.update(
        tender.id, **update_model.model_dump(exclude_none=True)
    )

    return new_version.as_model()


@router.put("/api/tenders/{tender_id}/rollback/{version}")
def rollback_to_version(
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    tender: Annotated[Tender, Depends(validate_access)],
    version: TenderVersionField,
) -> TenderModel:
    old_version = tender_repo.get_version_by_id(tender.id, version)

    return update_tender(
        tender_repo,
        tender,
        TenderUpdateModel(
            **{key: getattr(old_version, key) for key in TenderUpdateModel.model_fields}
        ),
    )
