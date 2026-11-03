from pydantic import BaseModel, ConfigDict


class StrictAPIModel(BaseModel):
    """Строго валидирует JSON-типы, не коэрсируя исходные значения ответа."""

    model_config = ConfigDict(strict=True)


class Country(StrictAPIModel):
    name: str
    code: str

class RegionItem(StrictAPIModel):
    id: int
    name: str
    code: str
    country: Country

class RegionResponse(StrictAPIModel):
    total: int
    items: list[RegionItem]

class RegionError(StrictAPIModel):
    id: str
    message: str

class RegionErrorResponse(StrictAPIModel):
    error: RegionError
