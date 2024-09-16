from avito_sep24.database import RawBase, engine

from .bid import Bid, BidDecision, BidVersion
from .bid_review import BidReview
from .employee import Employee
from .organization import Organization, OrganizationResponsible
from .tender import Tender, TenderVersion

__all__ = [
    "Employee",
    "Organization",
    "OrganizationResponsible",
    "Tender",
    "TenderVersion",
    "Bid",
    "BidVersion",
    "BidReview",
    "BidDecision",
]


RawBase.metadata.create_all(engine)
