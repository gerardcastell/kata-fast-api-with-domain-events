import uuid
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Customer(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    activePoliciesCount: int = Field(default=0)

    @field_validator('id', mode='before')
    @classmethod
    def generate_id_if_none(cls, v):
        if v is None:
            return str(uuid.uuid4())
        return v
