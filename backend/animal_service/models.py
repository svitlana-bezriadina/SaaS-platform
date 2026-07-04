# animal_service/models.py

from datetime import date, datetime
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text, Boolean, DateTime, Float
from sqlalchemy.orm import declarative_base
from database import EncryptedPhoneNumber

Base = declarative_base()

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
    __tablename__ = "settings"

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