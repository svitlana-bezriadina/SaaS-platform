# animal_service/models.py

from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, Boolean, DateTime, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime
from database import EncryptedPhoneNumber

Base = declarative_base()

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
    __tablename__ = "settings"
    
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