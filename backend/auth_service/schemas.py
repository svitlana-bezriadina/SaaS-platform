from typing import Optional

from pydantic import BaseModel, EmailStr, Field

class RegisterRequest(BaseModel):
    name: str
    org_type: str
    full_name: str
    admin_email: EmailStr
    password: str
    subdomain: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class OrganizationPublicResponse(BaseModel):
    id: int
    name: str
    org_type: str
    schema_name: str
    subdomain: Optional[str] = None

    class Config:
        orm_mode = True

class SubdomainUpdate(BaseModel):
    subdomain: str

class WorkerCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone_number: Optional[str] = Field(default=None, max_length=15)

class WorkerResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    organization_id: int
    phone_number: Optional[str] = Field(default=None, max_length=15)

    class Config:
        orm_mode = True