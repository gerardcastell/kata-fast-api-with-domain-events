import uuid
from pydantic import BaseModel, ConfigDict, Field


class Customer(BaseModel):
    model_config = ConfigDict(frozen=True)
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4())
    )  # Default value is a function that generates a new UUID
    name: str
    email: str
    activePoliciesCount: int = Field(default=0)
