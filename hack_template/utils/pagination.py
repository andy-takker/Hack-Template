from pydantic import BaseModel


class MetaPaginationModel(BaseModel):
    total: int
    limit: int
    offset: int
