from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

class BookingCreate(BaseModel):
    pet_id: int
    aviary_id: int
    start_date: date
    end_date: date
    status: Optional[str] = "confirmed"

class BookingResponse(BookingCreate):
    id: int
    total_price: float
    payment_status: str

    class Config:
        from_attributes = True

# Схема для "Мега-ендпоінта" бронювання
class BookingFullCreate(BaseModel):
    pet_id: Optional[int] = None
    pet_name: str
    species: str
    owner_name: str
    owner_phone: Optional[str] = Field(default=None, max_length=15)
    description: Optional[str] = None

    aviary_id: int
    start_date: date
    end_date: date

    service_ids: List[int] = []

class BookingUpdate(BaseModel):
    status: str
    payment_status: str
    service_ids: List[int] = []

class BookingStatusUpdate(BaseModel):
    status: str
    payment_status: Optional[str] = None

class AviaryCreate(BaseModel):
    number: str
    category: str
    daily_price: float
    status: Optional[str] = "available"

class AviaryResponse(BaseModel):
    id: int
    number: str
    category: str
    daily_price: float
    status: str

    class Config:
        from_attributes = True

class HotelPetCreate(BaseModel):
    name: str
    species: str
    owner_name: str
    owner_phone: Optional[str] = Field(default=None, max_length=15)
    description: Optional[str] = None

class HotelPetResponse(BaseModel):
    id: int
    name: str
    species: str
    owner_name: str
    owner_phone: Optional[str] = Field(default=None, max_length=15)
    description: Optional[str] = None

    class Config:
        from_attributes = True

class HotelTaskCreate(BaseModel):
    title: str
    date_time: datetime
    booking_id: Optional[int] = None
    description: Optional[str] = None
    repeat_days: Optional[int] = None
    recurrence_group_id: Optional[str] = None

class HotelTaskUpdate(BaseModel):
    title: Optional[str] = None
    date_time: Optional[datetime] = None
    booking_id: Optional[int] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    repeat_days: Optional[int] = None
    recurrence_group_id: Optional[str] = None

class HotelTaskResponse(BaseModel):
    id: int
    title: str
    date_time: datetime
    booking_id: Optional[int] = None
    description: Optional[str] = None
    is_completed: bool
    pet_id: Optional[int] = None
    pet_name: Optional[str] = None
    recurrence_group_id: Optional[str] = None

    class Config:
        from_attributes = True

class HotelSettingsResponse(BaseModel):
    id: int
    billing_mode: str
    hero_title: Optional[str] = None
    about_text: Optional[str] = None
    contact_phone: Optional[str] = Field(default=None, max_length=15)
    contact_email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True

class HotelSiteResponse(BaseModel):
    settings: HotelSettingsResponse
    aviaries: List[AviaryResponse]

    class Config:
        from_attributes = True

class HotelSettingsUpdate(BaseModel):
    billing_mode: str
    hero_title: Optional[str] = None
    about_text: Optional[str] = None
    contact_phone: Optional[str] = Field(default=None, max_length=15)
    contact_email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None

class ImageUploadResponse(BaseModel):
    url: str
    public_id: str

    class Config:
        from_attributes = True

class ServiceCreate(BaseModel):
    name: str
    price: float
    is_active: Optional[bool] = True

class ServiceResponse(BaseModel):
    id: int
    name: str
    price: float
    is_active: bool

    class Config:
        from_attributes = True

class BookingRequestCreate(BaseModel):
    pet_name: str
    species: str
    owner_name: str
    owner_phone: Optional[str] = Field(default=None, max_length=15)
    description: Optional[str] = None
    aviary_id: int
    start_date: date
    end_date: date
    service_ids: List[int] = []

class BookingRequestResponse(BaseModel):
    id: int
    pet_name: str
    species: str
    owner_name: str
    owner_phone: Optional[str] = Field(default=None, max_length=15)
    description: Optional[str] = None
    aviary_id: int
    start_date: date
    end_date: date
    status: str
    total_price: float
    created_at: datetime
    services: Optional[str] = None

    class Config:
        from_attributes = True

class BookingRequestUpdateStatus(BaseModel):
    status: str  # approved or rejected