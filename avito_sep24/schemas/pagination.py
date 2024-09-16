from typing import Annotated

from pydantic import Field

PaginationLimit = Annotated[int, Field(ge=0, le=50)]
PaginationOffset = Annotated[int, Field(ge=0)]
