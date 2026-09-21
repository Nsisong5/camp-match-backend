
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from typing import List, Optional

class PropertyResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    provider_id: UUID
    property_type: str
    name: str
    description: Optional[str]
    address: str
    latitude: float
    longitude: float
    campus_id: Optional[UUID]
    status: str

from camp_match.modules.housing.domain.value_objects import PropertyType, Currency, BillingPeriod

class CreatePropertySchema(BaseModel):
    property_type: PropertyType
    name: str
    description: Optional[str] = None
    address: str
    latitude: float
    longitude: float
    campus_id: Optional[UUID] = None

class UpdatePropertySchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    has_water: Optional[bool] = None
    has_electricity: Optional[bool] = None
    has_security: Optional[bool] = None
    has_parking: Optional[bool] = None
    has_generator: Optional[bool] = None
    has_cctv: Optional[bool] = None
    has_wifi: Optional[bool] = None

class UnitResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    property_id: UUID
    label: str
    total_capacity: int
    occupied_count: int
    is_furnished: bool
    has_private_bathroom: bool
    has_kitchen: bool

class CreateUnitSchema(BaseModel):
    label: str
    total_capacity: int = Field(gt=0)
    is_furnished: bool = False
    has_private_bathroom: bool = False
    has_kitchen: bool = False

class UpdateUnitSchema(BaseModel):
    label: Optional[str] = None
    total_capacity: Optional[int] = Field(None, gt=0)
    is_furnished: Optional[bool] = None
    has_private_bathroom: Optional[bool] = None
    has_kitchen: Optional[bool] = None

class PriceSchema(BaseModel):
    amount_kobo: int
    currency: str
    period: str

class ListingResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    property_id: UUID
    unit_id: UUID
    title: str
    description: Optional[str]
    price: PriceSchema
    status: str

class CreateListingSchema(BaseModel):
    property_id: UUID
    unit_id: UUID
    title: str
    description: Optional[str] = None
    price_amount_kobo: int = Field(ge=0)
    price_currency: Currency
    price_period: BillingPeriod

class UpdateListingSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price_amount_kobo: Optional[int] = Field(None, ge=0)

class AvailabilityResponseSchema(BaseModel):
    available_count: int

class PropertyPageSchema(BaseModel):
    items: List[PropertyResponseSchema]
    total: int
    page: int
    page_size: int
