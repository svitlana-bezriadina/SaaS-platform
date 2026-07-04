# auth_service/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import models 
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESSIV
from sqlalchemy.types import TypeDecorator, String

# Підключення до бази з docker-compose
SQLALCHEMY_DATABASE_URL = "postgresql://admin:2321919458@db:5432/petcloud"
SECRET_KEY = b'89dh81ggf83hmckw9ejcl9j3ncijs927'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- database.py ---
def create_tenant_schema(schema_name: str, org_type: str):
    with engine.connect() as connection:
        connection.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}";'))
        connection.execute(text(f'SET search_path TO "{schema_name}";'))
        
        if org_type == "shelter":
            tables_to_create = [
                models.ShelterAnimal.__table__, 
                models.MedicalRecord.__table__, 
                models.ShelterTask.__table__,
                models.ShelterInventory.__table__,
                models.SiteSettings.__table__
            ]
        elif org_type == "hotel":
            tables_to_create = [
                models.HotelPet.__table__, 
                models.Aviary.__table__, 
                models.Service.__table__, 
                models.Booking.__table__, 
                models.BookingServiceLink.__table__,
                models.BookingRequest.__table__,
                models.HotelTask.__table__,
                models.HotelSettings.__table__
            ]
        else:
            raise ValueError("Невідомий тип організації")

        models.Base.metadata.create_all(bind=connection, tables=tables_to_create)
        connection.commit()

def get_cipher():
    return AESSIV(SECRET_KEY)

def encrypt_deterministic(plaintext: str) -> str:
    if not plaintext:
        return plaintext
    cipher = get_cipher()
    # AES-SIV вимагає список associated_data, передаємо None
    ciphertext = cipher.encrypt(plaintext.encode('utf-8'), None)
    return base64.urlsafe_b64encode(ciphertext).decode('utf-8')

def decrypt_deterministic(ciphertext: str) -> str:
    if not ciphertext:
        return ciphertext
    try:
        cipher = get_cipher()
        decoded = base64.urlsafe_b64decode(ciphertext.encode('utf-8'))
        plaintext = cipher.decrypt(decoded, None)
        return plaintext.decode('utf-8')
    except Exception:
        # Якщо розшифрувати не вдалося (наприклад, старі нешифровані дані)
        return ciphertext

# === КАСТОМНИЙ ТИП ДЛЯ SQLALCHEMY ===
class EncryptedPhoneNumber(TypeDecorator):
    """
    Кастомний тип, який автоматично шифрує дані перед записом у БД 
    та розшифровує їх після зчитування.
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        # Відбувається ПЕРЕД записом в БД або при пошуку (filter)
        return encrypt_deterministic(value)

    def process_result_value(self, value, dialect):
        # Відбувається ПІСЛЯ зчитування з БД
        return decrypt_deterministic(value)