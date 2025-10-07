import uuid

from sqlmodel import Field, SQLModel


class Customer(SQLModel, table=True):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True
    )
    name: str
    email: str
    activePoliciesCount: int = Field(default=0)
