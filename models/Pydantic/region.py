from pydantic import BaseModel


class Country(BaseModel):
    name: str
    code: str

class RegionItem(BaseModel):
    id: int
    name: str
    code: str
    country: Country

class RegionResponse(BaseModel):
    total: int
    items: list[RegionItem]

class RegionError(BaseModel):
    id: str
    message: str

class RegionErrorResponse(BaseModel):
    error: RegionError