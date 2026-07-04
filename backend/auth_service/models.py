# auth_service/models.py
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, Boolean, DateTime, Float
from sqlalchemy.orm import declarative_base
from database import EncryptedPhoneNumber

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organizations"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    org_type = Column(String)
    schema_name = Column(String, unique=True)
    subdomain = Column(String, unique=True, index=True, nullable=True)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "public"}

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("public.organizations.id"))
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="admin")
    phone_number = Column(EncryptedPhoneNumber, nullable=True)


#----------HOTEL MODELS----------
class ShelterAnimal(Base):
    __tablename__ = "shelter_animals"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    species = Column(String)
    date_register = Column(Date, default=date.today)
    description = Column(Text)
    photo_url = Column(String)
    is_public = Column(Boolean, default=False)
    health_status = Column(String, default="Здоровий")

class SiteSettings(Base):
    __tablename__ = "shelter_settings"

    id = Column(Integer, primary_key=True)
    hero_title = Column(String, nullable=True)
    about_text = Column(Text, nullable=True)
    contact_phone = Column(EncryptedPhoneNumber, nullable=True)
    contact_email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)

class MedicalRecord(Base):
    __tablename__ = "medical_records"
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("shelter_animals.id"))
    record_date = Column(Date)
    type = Column(String)
    notes = Column(Text)

class ShelterTask(Base):
    __tablename__ = "shelter_tasks"
    id = Column(Integer, primary_key=True)
    animal_id = Column(Integer, ForeignKey("shelter_animals.id"))
    date_time = Column(DateTime)
    title = Column(String)
    recurrence_group_id = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)

class ShelterInventory(Base):
    __tablename__ = "shelter_inventory"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Float, default=0.0)  
    target_quantity = Column(Float, default=0.0)
    target_animal = Column(String, nullable=True)
    unit = Column(String, nullable=False)



#----------HOTEL MODELS----------
class HotelPet(Base):
    __tablename__ = "hotel_pets"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    species = Column(String)
    owner_name = Column(String)
    owner_phone = Column(EncryptedPhoneNumber)
    description = Column(Text)

class Aviary(Base):
    __tablename__ = "aviaries"
    id = Column(Integer, primary_key=True)
    number = Column(String)
    category = Column(String) # Стандарт, VIP
    daily_price = Column(Float)
    status = Column(String)

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    is_active = Column(Boolean, default=True)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("hotel_pets.id"))
    aviary_id = Column(Integer, ForeignKey("aviaries.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String)
    total_price = Column(Float, default=0.0)
    payment_status = Column(String, default="Не оплачено")

class BookingServiceLink(Base):
    __tablename__ = "booking_services"
    booking_id = Column(Integer, ForeignKey("bookings.id"), primary_key=True)
    service_id = Column(Integer, ForeignKey("services.id"), primary_key=True)

class HotelTask(Base):
    __tablename__ = "hotel_tasks"
    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings.id")) 
    date_time = Column(DateTime)
    title = Column(String) 
    description = Column(Text)
    is_completed = Column(Boolean, default=False)
    recurrence_group_id = Column(String, nullable=True)

class HotelSettings(Base):
    __tablename__ = "hotel_settings"
    
    id = Column(Integer, primary_key=True)
    billing_mode = Column(String, default="nights")
    hero_title = Column(String, nullable=True)
    about_text = Column(Text, nullable=True)
    contact_phone = Column(EncryptedPhoneNumber, nullable=True)
    contact_email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    cover_image_url = Column(String, nullable=True)

class BookingRequest(Base):
    __tablename__ = "booking_requests"
    id = Column(Integer, primary_key=True)
    pet_name = Column(String)
    species = Column(String)
    owner_name = Column(String)
    owner_phone = Column(EncryptedPhoneNumber)
    description = Column(Text, nullable=True)
    aviary_id = Column(Integer, ForeignKey("aviaries.id"))
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String, default="pending")
    total_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    services = Column(Text, nullable=True)