from sqlmodel import Field, SQLModel


class CustomerModel(SQLModel, table=True):
    __tablename__ = 'customer'
    id: str = Field(primary_key=True)
    name: str = Field()
    email: str = Field(index=True)
    activePoliciesCount: int = Field()
