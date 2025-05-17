from pydantic import BaseModel, Field
from typing import Annotated

class Review(BaseModel):
    review: Annotated[int, Field(ge=1, le=5)]
