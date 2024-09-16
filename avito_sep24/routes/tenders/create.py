import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from avito_sep24.errors import ClientRequestError, assert401, assert403
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
    TenderCreateModel,
    TenderModel,
)

router = APIRouter()


@router.post("/api/tenders/new")
def create_new_tender(
    model: TenderCreateModel,
    tender_repo: Annotated[TenderRepository, Depends(get_tender_repository)],
    employee_repo: Annotated[EmployeeRepository, Depends(get_employee_repository)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repository)],
) -> TenderModel:
    creator = employee_repo.find_by_username(model.creator_username)
    assert401(creator is not None, "no employee found with such username")

    try:
        organization_id = uuid.UUID(model.organization_id)
        organization = org_repo.find_by_id(organization_id)
    except ValueError as e:
        raise ClientRequestError(401, "invalid organization id") from e

    assert401(organization is not None, "no such organization")

    is_responsible = org_repo.is_responsible(organization.id, creator.id)
    assert403(is_responsible, "you are not responsible for this organization")

    tender_version = tender_repo.create_as_version(
        name=model.name,
        description=model.description,
        service_type=model.service_type,
        organization_id=organization.id,
        creator_id=creator.id,
    )

    return tender_version.as_model()
