from pydantic import BaseModel


class Tool(BaseModel):
    id: int
    name: str
    description: str
    cost: float
    owner_id: int
    url: str