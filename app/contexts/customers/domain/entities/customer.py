import uuid

from pydantic import BaseModel, Field


class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    activePoliciesCount: int = Field(default=0)
