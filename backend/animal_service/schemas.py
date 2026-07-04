from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, List

class AnimalCreate(BaseModel):
    name: str
    age: int
    species: str
    description: Optional[str] = None
    photo_url: Optional[str] = None
    health_status: Optional[str] = None
    is_public: Optional[bool] = False

class AnimalResponse(AnimalCreate):
    id: int
    date_register: Optional[date] = None

    class Config:
        from_attributes = True

class SiteSettingsResponse(BaseModel):
    id: int
    hero_title: Optional[str] = None
    about_text: Optional[str] = None
    contact_phone: Optional[str] = Field(default=None, max_length=15)
    contact_email: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None

    class Config:
        from_attributes = True

class SiteSettingsUpdate(BaseModel):
    hero_title: Optional[str] = None
    about_text: Optional[str] = None
    contact_phone: Optional[str] = Field(default=None, max_length=15)
    contact_email: Optional[str] = Field(default=None, max_length=15) 
    address: Optional[str] = None
    logo_url: Optional[str] = None
    cover_image_url: Optional[str] = None

class PublicSiteResponse(BaseModel):
    settings: SiteSettingsResponse
    animals: List[AnimalResponse]

    class Config:
        from_attributes = True

class ImageUploadResponse(BaseModel):
    url: str
    public_id: str

    class Config:
        from_attributes = True

class MedicalRecordBase(BaseModel):
    record_date: date
    type: str
    notes: Optional[str] = None
    animal_id: int

class MedicalRecordCreate(MedicalRecordBase):
    pass

class MedicalRecordUpdate(BaseModel):
    record_date: Optional[date] = None
    type: Optional[str] = None
    notes: Optional[str] = None

class MedicalRecord(MedicalRecordBase):
    id: int

    class Config:
        from_attributes = True

# Shelter Tasks Schemas
class ShelterTaskCreate(BaseModel):
    title: str
    date_time: datetime
    animal_id: Optional[int] = None
    repeat_days: Optional[int] = None
    recurrence_group_id: Optional[str] = None

class ShelterTaskUpdate(BaseModel):
    title: Optional[str] = None
    date_time: Optional[datetime] = None
    is_completed: Optional[bool] = None
    animal_id: Optional[int] = None
    repeat_days: Optional[int] = None
    recurrence_group_id: Optional[str] = None

class ShelterTaskResponse(BaseModel):
    id: int
    title: str
    date_time: datetime
    is_completed: bool
    animal_id: Optional[int] = None
    animal_name: Optional[str] = None
    recurrence_group_id: Optional[str] = None

    class Config:
        from_attributes = True

# Shelter Inventory Schemas
class ShelterInventoryBase(BaseModel):
    name: str
    category: str
    quantity: float
    target_quantity: float
    target_animal: Optional[str] = None
    unit: str

class ShelterInventoryCreate(ShelterInventoryBase):
    pass

class ShelterInventoryUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    target_quantity: Optional[float] = None
    target_animal: Optional[str] = None
    unit: Optional[str] = None

class ShelterInventoryResponse(ShelterInventoryBase):
    id: int

    class Config:
        from_attributes = True