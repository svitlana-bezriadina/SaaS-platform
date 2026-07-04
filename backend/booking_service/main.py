import os
from datetime import date, datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Header, Query, File, UploadFile
from sqlalchemy import and_, text, or_
from sqlalchemy.orm import Session
from typing import List
import uuid
import cloudinary
import cloudinary.uploader
import models, schemas
from database import SessionLocal, engine
from jose import JWTError, jwt
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PetCloud Booking Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

auth_scheme = HTTPBearer()

SECRET_KEY = "diploma_super_secret_key_change_me_later"
ALGORITHM = "HS256"

def get_tenant_schema(token: str = Depends(auth_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("schema_name")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_token_payload(token: str = Depends(auth_scheme)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_admin(payload: dict = Depends(get_token_payload)):
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Тільки для адміністраторів")
    return payload


def configure_cloudinary():
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")
    if not cloud_name or not api_key or not api_secret:
        raise RuntimeError("Cloudinary credentials are not set in environment variables")
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True
    )


def upload_image_to_cloudinary(file: UploadFile, folder: str):
    file_content = file.file.read()
    result = cloudinary.uploader.upload(
        file_content,
        folder=folder,
        resource_type="image"
    )
    return result


configure_cloudinary()


def get_db(schema_name: str = Depends(get_tenant_schema)):
    db = SessionLocal()
    try:
        db.execute(text(f'SET search_path TO "{schema_name}"'))
        yield db
    finally:
        db.close()


def get_public_db(schema_name: str = Query(..., min_length=1)):
    db = SessionLocal()
    try:
        db.execute(text(f'SET search_path TO "{schema_name}"'))
        yield db
    finally:
        db.close()


@app.get("/public/settings", response_model=schemas.HotelSettingsResponse)
def get_public_settings(schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    if not settings:
        settings = models.HotelSettings(id=1, billing_mode="nights")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@app.get("/public/aviaries", response_model=List[schemas.AviaryResponse])
def get_public_aviaries(schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    return db.query(models.Aviary).filter(models.Aviary.status != "Виведений з експлуатації").all()


@app.get("/public/aviaries/available", response_model=List[schemas.AviaryResponse])
def get_public_available_aviaries(start_date: date, end_date: date, schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    booked_aviary_ids = db.query(models.Booking.aviary_id).filter(
        models.Booking.status != "Скасоване",
        models.Booking.start_date <= end_date,
        models.Booking.end_date >= start_date
    ).all()
    forbidden_ids = [item[0] for item in booked_aviary_ids]
    query = db.query(models.Aviary).filter(models.Aviary.status != "Виведений з експлуатації")
    if forbidden_ids:
        query = query.filter(~models.Aviary.id.in_(forbidden_ids))
    return query.all()


@app.get("/public/site", response_model=schemas.HotelSiteResponse)
def get_public_site(schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    if not settings:
        settings = models.HotelSettings(id=1, billing_mode="nights")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    aviaries = db.query(models.Aviary).filter(models.Aviary.status != "Виведений з експлуатації").all()
    return {"settings": settings, "aviaries": aviaries}


@app.get("/public/hotel/site", response_model=schemas.HotelSiteResponse)
def get_public_hotel_site(schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    return get_public_site(schema_name, db)


@app.post("/public/bookings/full", response_model=schemas.BookingResponse)
def create_public_booking(data: schemas.BookingFullCreate, schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    db.expire_on_commit = False

    if data.pet_id:
        pet = db.query(models.HotelPet).filter(models.HotelPet.id == data.pet_id).first()
        if not pet:
            raise HTTPException(status_code=404, detail="Тварину не знайдено")
        pet.name = data.pet_name
        pet.species = data.species
        pet.owner_name = data.owner_name
        pet.owner_phone = data.owner_phone
        pet.description = data.description
    else:
        pet = models.HotelPet(
            name=data.pet_name,
            species=data.species,
            owner_name=data.owner_name,
            owner_phone=data.owner_phone,
            description=data.description
        )
        db.add(pet)
        db.flush()

    conflict = db.query(models.Booking).filter(
        models.Booking.aviary_id == data.aviary_id,
        models.Booking.status != "Скасоване",
        models.Booking.start_date <= data.end_date,
        models.Booking.end_date >= data.start_date
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="Цей вольєр вже зайнятий на обрані дати")

    hotel_settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    billing_mode = hotel_settings.billing_mode if hotel_settings else "nights"

    days = (data.end_date - data.start_date).days
    if billing_mode == "days":
        days += 1
    if days <= 0:
        days = 1

    aviary = db.query(models.Aviary).filter(models.Aviary.id == data.aviary_id).first()
    if not aviary:
        raise HTTPException(status_code=404, detail="Вольєр не знайдено")
    total_price = aviary.daily_price * days

    if data.service_ids:
        services = db.query(models.Service).filter(models.Service.id.in_(data.service_ids)).all()
        for s in services:
            total_price += s.price

    booking = models.Booking(
        pet_id=pet.id,
        aviary_id=data.aviary_id,
        start_date=data.start_date,
        end_date=data.end_date,
        status="pending",
        total_price=total_price,
        payment_status="Не оплачено"
    )
    db.add(booking)
    db.flush()

    if data.service_ids:
        for service_id in data.service_ids:
            link = models.BookingServiceLink(booking_id=booking.id, service_id=service_id)
            db.add(link)

    db.commit()
    return booking


@app.get("/public/services", response_model=List[schemas.ServiceResponse])
def get_public_services(schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    return db.query(models.Service).filter(models.Service.is_active == True).all()


@app.patch("/bookings/{id}/status", response_model=schemas.BookingResponse)
def update_booking_status(id: int, data: schemas.BookingStatusUpdate, db: Session = Depends(get_db)):
    db.expire_on_commit = False

    booking = db.query(models.Booking).filter(models.Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")

    booking.status = data.status
    if data.payment_status is not None:
        booking.payment_status = data.payment_status

    db.commit()
    db.refresh(booking)
    return booking


# --- Ендпоінти для вольєрів ---
@app.post("/aviaries", response_model=schemas.AviaryResponse)
def create_aviary(aviary: schemas.AviaryCreate, db: Session = Depends(get_db)):
    db.expire_on_commit = False

    db_aviary = models.Aviary(**aviary.model_dump())
    db.add(db_aviary)
    db.commit()
    return db_aviary

@app.get("/aviaries", response_model=List[schemas.AviaryResponse])
def list_aviaries(db: Session = Depends(get_db)):
    return db.query(models.Aviary).all()

@app.put("/aviaries/{id}", response_model=schemas.AviaryResponse)
def update_aviary(id: int, aviary_data: schemas.AviaryCreate, db: Session = Depends(get_db)):
    db.expire_on_commit = False

    db_aviary = db.query(models.Aviary).filter(models.Aviary.id == id).first()
    if not db_aviary:
        raise HTTPException(status_code=404, detail="Вольєр не знайдено")
    
    db_aviary.number = aviary_data.number
    db_aviary.category = aviary_data.category
    db_aviary.daily_price = aviary_data.daily_price
    db_aviary.status = aviary_data.status
    
    db.commit()
    return db_aviary

@app.delete("/aviaries/{id}")
def soft_delete_aviary(id: int, db: Session = Depends(get_db)):
    db_aviary = db.query(models.Aviary).filter(models.Aviary.id == id).first()
    if not db_aviary:
        raise HTTPException(status_code=404, detail="Вольєр не знайдено")
    
    db_aviary.status = "Виведений з експлуатації"
    db.commit()
    return {"message": "Вольєр архівовано"}

@app.get("/aviaries/available", response_model=List[schemas.AviaryResponse])
def get_available_aviaries(start_date: date, end_date: date, db: Session = Depends(get_db)):
    booked_aviary_ids = db.query(models.Booking.aviary_id).filter(
        models.Booking.status != "Скасоване",
        models.Booking.start_date <= end_date,
        models.Booking.end_date >= start_date
    ).all()
    
    forbidden_ids = [item[0] for item in booked_aviary_ids]
    
    if not forbidden_ids:
        return db.query(models.Aviary).filter(models.Aviary.status != "Виведений з експлуатації").all()
        
    available_aviaries = db.query(models.Aviary).filter(
        ~models.Aviary.id.in_(forbidden_ids),
        models.Aviary.status != "Виведений з експлуатації"
    ).all()
    
    return available_aviaries

# --- Ендпоінти для бронювань ---
@app.post("/bookings/full", response_model=schemas.BookingResponse)
def create_full_booking(data: schemas.BookingFullCreate, db: Session = Depends(get_db)):
    db.expire_on_commit = False
    
    # 1. Знаходимо або створюємо клієнта
    if data.pet_id:
        pet = db.query(models.HotelPet).filter(models.HotelPet.id == data.pet_id).first()
        if not pet:
            raise HTTPException(status_code=404, detail="Тварину не знайдено")
        # Оновлюємо дані, якщо власник щось змінив (наприклад, додав опис)
        pet.name = data.pet_name
        pet.species = data.species
        pet.owner_name = data.owner_name
        pet.description = data.description
    else:
        # Новий клієнт
        pet = models.HotelPet(
            name=data.pet_name,
            species=data.species,
            owner_name=data.owner_name,
            owner_phone=data.owner_phone,
            description=data.description
        )
        db.add(pet)
        db.flush() # отримуємо pet.id, але поки не комітимо (якщо буде помилка далі - тварина не збережеться)
    
    # 2. Перевірка вольєра (захист від овербукінгу)
    conflict = db.query(models.Booking).filter(
        models.Booking.aviary_id == data.aviary_id,
        models.Booking.status != "Скасоване",
        models.Booking.start_date <= data.end_date,
        models.Booking.end_date >= data.start_date
    ).first()
    
    if conflict:
        raise HTTPException(status_code=400, detail="Цей вольєр вже зайнятий на обрані дати")
        
    # 3. Рахуємо ціну (Вольєр * Дні)
    hotel_settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    billing_mode = hotel_settings.billing_mode if hotel_settings else "nights"

    # Математика розрахунку днів
    days = (data.end_date - data.start_date).days
    
    if billing_mode == "days":
        days += 1 # Режим "За календарні дні" (Inclusive)

    if days <= 0:
        days = 1 # Запобіжник: мінімум 1 доба/день
        
    aviary = db.query(models.Aviary).filter(models.Aviary.id == data.aviary_id).first()
    total_price = aviary.daily_price * days
    
    # Додаємо ціну послуг
    if data.service_ids:
        services = db.query(models.Service).filter(models.Service.id.in_(data.service_ids)).all()
        for s in services:
            total_price += s.price
    
    # 4. Створюємо саме бронювання
    booking = models.Booking(
        pet_id=pet.id,
        aviary_id=data.aviary_id,
        start_date=data.start_date,
        end_date=data.end_date,
        status="Актуальне",
        total_price=total_price,
        payment_status="Не оплачено"
    )
    db.add(booking)
    db.flush() # Отримуємо booking.id для прив'язки послуг
    
    # 5. Прив'язуємо послуги (Many-to-Many)
    if data.service_ids:
        for service_id in data.service_ids:
            link = models.BookingServiceLink(booking_id=booking.id, service_id=service_id)
            db.add(link)
            
    # 6. Зберігаємо все разом (Тварину, Бронювання і Послуги)
    db.commit() 
    return booking

@app.get("/bookings", response_model=List[schemas.BookingResponse])
def list_bookings(db: Session = Depends(get_db)):
    return db.query(models.Booking).all()

@app.get("/bookings/{id}/services")
def get_booking_services(id: int, db: Session = Depends(get_db)):
    """Повертає масив ID послуг, які підключені до цього бронювання"""
    links = db.query(models.BookingServiceLink).filter(models.BookingServiceLink.booking_id == id).all()
    return [link.service_id for link in links]

@app.put("/bookings/{id}", response_model=schemas.BookingResponse)
def update_booking(id: int, data: schemas.BookingUpdate, db: Session = Depends(get_db)):
    db.expire_on_commit = False
    booking = db.query(models.Booking).filter(models.Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")
    
    # 1. Оновлюємо базові статуси
    booking.status = data.status
    booking.payment_status = data.payment_status
    
    # 2. Оновлюємо послуги (видаляємо старі зв'язки, створюємо нові)
    db.query(models.BookingServiceLink).filter(models.BookingServiceLink.booking_id == id).delete()
    for s_id in data.service_ids:
        db.add(models.BookingServiceLink(booking_id=id, service_id=s_id))
        
    # 3. Перераховуємо загальну вартість (з урахуванням налаштувань)
    hotel_settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    billing_mode = hotel_settings.billing_mode if hotel_settings else "nights"

    days = (booking.end_date - booking.start_date).days
    if billing_mode == "days":
        days += 1
    if days <= 0:
        days = 1
        
    aviary = db.query(models.Aviary).filter(models.Aviary.id == booking.aviary_id).first()
    total_price = aviary.daily_price * days
    
    if data.service_ids:
        services = db.query(models.Service).filter(models.Service.id.in_(data.service_ids)).all()
        for s in services:
            total_price += s.price
            
    booking.total_price = total_price
    db.commit()
    return booking

@app.delete("/bookings/{id}")
def delete_booking(id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")
        
    # Спочатку видаляємо зв'язки з послугами (щоб не було помилки ForeignKey)
    db.query(models.BookingServiceLink).filter(models.BookingServiceLink.booking_id == id).delete()
    
    db.delete(booking)
    db.commit()
    return {"message": "Бронювання видалено"}

# --- Ендпоінти для тварин у готелі ---
@app.post("/hotel_pets", response_model=schemas.HotelPetResponse)
def create_hotel_pet(pet: schemas.HotelPetCreate, db: Session = Depends(get_db)):
    db.expire_on_commit = False

    db_pet = models.HotelPet(**pet.model_dump())
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet

@app.get("/hotel_pets", response_model=List[schemas.HotelPetResponse])
def list_hotel_pets(db: Session = Depends(get_db)):
    """Повертає список усіх клієнтів (тварин) готелю"""
    return db.query(models.HotelPet).all()

@app.get("/hotel_tasks", response_model=List[schemas.HotelTaskResponse])
def list_hotel_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.HotelTask).all()
    result = []
    for task in tasks:
        item = {
            "id": task.id,
            "title": task.title,
            "date_time": task.date_time,
            "booking_id": task.booking_id,
            "description": task.description,
            "is_completed": task.is_completed,
            "recurrence_group_id": task.recurrence_group_id,
            "pet_id": None,
            "pet_name": None
        }
        if task.booking_id:
            booking = db.query(models.Booking).filter(models.Booking.id == task.booking_id).first()
            if booking:
                item["pet_id"] = booking.pet_id
                pet = db.query(models.HotelPet).filter(models.HotelPet.id == booking.pet_id).first()
                if pet:
                    item["pet_name"] = pet.name
        result.append(item)
    return result

@app.get("/hotel_tasks/due_soon", response_model=List[schemas.HotelTaskResponse])
def list_due_soon_hotel_tasks(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    soon = now + timedelta(hours=24)
    tasks = db.query(models.HotelTask).filter(
        models.HotelTask.is_completed == False,
        models.HotelTask.date_time <= soon
    ).order_by(models.HotelTask.date_time.asc()).all()

    result = []
    for task in tasks:
        item = {
            "id": task.id,
            "title": task.title,
            "date_time": task.date_time,
            "booking_id": task.booking_id,
            "description": task.description,
            "is_completed": task.is_completed,
            "recurrence_group_id": task.recurrence_group_id,
            "pet_id": None,
            "pet_name": None
        }
        if task.booking_id:
            booking = db.query(models.Booking).filter(models.Booking.id == task.booking_id).first()
            if booking:
                item["pet_id"] = booking.pet_id
                pet = db.query(models.HotelPet).filter(models.HotelPet.id == booking.pet_id).first()
                if pet:
                    item["pet_name"] = pet.name
        result.append(item)
    return result

@app.post("/hotel_tasks", response_model=schemas.HotelTaskResponse)
def create_hotel_task(task: schemas.HotelTaskCreate, db: Session = Depends(get_db)):
    db.expire_on_commit = False

    group_id = task.recurrence_group_id or str(uuid.uuid4())
    repeat_days = task.repeat_days or 1

    if repeat_days <= 1:
        db_task = models.HotelTask(
            title=task.title,
            date_time=task.date_time,
            booking_id=task.booking_id,
            description=task.description,
            recurrence_group_id=task.recurrence_group_id if task.recurrence_group_id else None
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return {
            "id": db_task.id,
            "title": db_task.title,
            "date_time": db_task.date_time,
            "booking_id": db_task.booking_id,
            "description": db_task.description,
            "is_completed": db_task.is_completed,
            "recurrence_group_id": db_task.recurrence_group_id,
            "pet_id": None,
            "pet_name": None
        }

    first_task = None
    for i in range(repeat_days):
        next_date = task.date_time + timedelta(days=i)
        db_task = models.HotelTask(
            title=task.title,
            date_time=next_date,
            booking_id=task.booking_id,
            description=task.description,
            recurrence_group_id=group_id
        )
        db.add(db_task)
        db.flush()
        if i == 0:
            first_task = db_task

    db.commit()
    db.refresh(first_task)
    return {
        "id": first_task.id,
        "title": first_task.title,
        "date_time": first_task.date_time,
        "booking_id": first_task.booking_id,
        "description": first_task.description,
        "is_completed": first_task.is_completed,
        "recurrence_group_id": first_task.recurrence_group_id,
        "pet_id": None,
        "pet_name": None
    }

@app.put("/hotel_tasks/{task_id}", response_model=schemas.HotelTaskResponse)
def update_hotel_task(task_id: int, task_update: schemas.HotelTaskUpdate, db: Session = Depends(get_db)):
    db.expire_on_commit = False

    db_task = db.query(models.HotelTask).filter(models.HotelTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Завдання не знайдено")
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.flush()
    db.commit()
    booking = db.query(models.Booking).filter(models.Booking.id == db_task.booking_id).first() if db_task.booking_id else None
    pet = db.query(models.HotelPet).filter(models.HotelPet.id == booking.pet_id).first() if booking else None
    return {
        "id": db_task.id,
        "title": db_task.title,
        "date_time": db_task.date_time,
        "booking_id": db_task.booking_id,
        "description": db_task.description,
        "is_completed": db_task.is_completed,
        "pet_id": pet.id if pet else None,
        "pet_name": pet.name if pet else None
    }

@app.delete("/hotel_tasks/{task_id}")
def delete_hotel_task(task_id: int, db: Session = Depends(get_db)):
    db.expire_on_commit = False

    db_task = db.query(models.HotelTask).filter(models.HotelTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Завдання не знайдено")
    db.delete(db_task)
    db.commit()
    return {"message": "Завдання видалено"}

@app.delete("/hotel_tasks/{task_id}/recurrence")
def cancel_hotel_task_recurrence(task_id: int, db: Session = Depends(get_db)):
    db.expire_on_commit = False

    current_task = db.query(models.HotelTask).filter(models.HotelTask.id == task_id).first()
    if not current_task:
        raise HTTPException(status_code=404, detail="Завдання не знайдено")

    if not current_task.recurrence_group_id:
        raise HTTPException(status_code=400, detail="Це завдання не є частиною серії повторень")

    deleted_count = db.query(models.HotelTask).filter(
        models.HotelTask.recurrence_group_id == current_task.recurrence_group_id,
        models.HotelTask.date_time >= current_task.date_time
    ).delete(synchronize_session=False)

    db.commit()
    return {"message": f"Повторення скасовано з цього дня. Видалено майбутніх завдань: {deleted_count}"}

@app.get("/hotel_pets/search", response_model=List[schemas.HotelPetResponse])
def search_pet_by_phone(phone: str, db: Session = Depends(get_db)):
    pets = db.query(models.HotelPet).filter(models.HotelPet.owner_phone == phone).all()
    return pets

# --- Ендпоінти для Прайс-листа (Послуги) ---

# Отримати ВСІ послуги (і активні, і архівовані - для адмін-панелі)
@app.get("/services/all", response_model=List[schemas.ServiceResponse])
def get_all_services(db: Session = Depends(get_db)):
    return db.query(models.Service).all()

@app.get("/services")
def list_services(db: Session = Depends(get_db)):
    return db.query(models.Service).filter(models.Service.is_active == True).all()

@app.post("/services", response_model=schemas.ServiceResponse)
def create_service(service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db.expire_on_commit = False
    db_service = models.Service(**service.model_dump())
    db.add(db_service)
    db.commit()
    return db_service

@app.put("/services/{id}", response_model=schemas.ServiceResponse)
def update_service(id: int, service: schemas.ServiceCreate, db: Session = Depends(get_db)):
    db.expire_on_commit = False
    db_service = db.query(models.Service).filter(models.Service.id == id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Послугу не знайдено")
    
    db_service.name = service.name
    db_service.price = service.price
    db_service.is_active = service.is_active
    db.commit()
    return db_service

@app.delete("/services/{id}")
def soft_delete_service(id: int, db: Session = Depends(get_db)):
    db.expire_on_commit = False
    db_service = db.query(models.Service).filter(models.Service.id == id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail="Послугу не знайдено")
    
    # Soft Delete: просто ховаємо послугу з актуального прайсу
    db_service.is_active = False 
    db.commit()
    return {"message": "Послугу архівовано"}

@app.get("/settings", response_model=schemas.HotelSettingsResponse)
def get_hotel_settings(db: Session = Depends(get_db)):
    settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    if not settings:
        settings = models.HotelSettings(id=1, billing_mode="nights")
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@app.post("/settings/upload", response_model=schemas.ImageUploadResponse)
def upload_hotel_image(file: UploadFile = File(...), _admin: dict = Depends(require_admin)):
    result = upload_image_to_cloudinary(file, folder="petcloud/hotel")
    return {"url": result["secure_url"], "public_id": result["public_id"]}

@app.put("/settings", response_model=schemas.HotelSettingsResponse)
def update_hotel_settings(data: schemas.HotelSettingsUpdate, db: Session = Depends(get_db)):
    db.expire_on_commit = False
    settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    if not settings:
        settings = models.HotelSettings(id=1)
        db.add(settings)
    
    settings.billing_mode = data.billing_mode
    if data.hero_title is not None:
        settings.hero_title = data.hero_title
    if data.about_text is not None:
        settings.about_text = data.about_text
    if data.contact_phone is not None:
        settings.contact_phone = data.contact_phone
    if data.contact_email is not None:
        settings.contact_email = data.contact_email
    if data.address is not None:
        settings.address = data.address
    if data.logo_url is not None:
        settings.logo_url = data.logo_url
    if data.cover_image_url is not None:
        settings.cover_image_url = data.cover_image_url

    db.commit()
    return settings


# --- Ендпоінти для Заявок на Бронювання (лівня Approval) ---

@app.post("/public/booking-requests", response_model=schemas.BookingRequestResponse)
def create_booking_request(data: schemas.BookingRequestCreate, schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    """Створює заявку на бронювання (потребує одобрення адміністратором)"""
    db.expire_on_commit = False
    
    # Перевіряємо наявність вольєра
    aviary = db.query(models.Aviary).filter(models.Aviary.id == data.aviary_id).first()
    if not aviary:
        raise HTTPException(status_code=404, detail="Вольєр не знайдено")
    
    # Розраховуємо ціну
    hotel_settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    billing_mode = hotel_settings.billing_mode if hotel_settings else "nights"
    
    days = (data.end_date - data.start_date).days
    if billing_mode == "days":
        days += 1
    if days <= 0:
        days = 1
    
    total_price = aviary.daily_price * days
    
    # Додаємо ціну послуг
    services_json = ""
    if data.service_ids:
        services = db.query(models.Service).filter(models.Service.id.in_(data.service_ids)).all()
        for s in services:
            total_price += s.price
        services_json = ",".join(str(s) for s in data.service_ids)
    
    # Створюємо заявку
    booking_request = models.BookingRequest(
        pet_name=data.pet_name,
        species=data.species,
        owner_name=data.owner_name,
        owner_phone=data.owner_phone,
        description=data.description,
        aviary_id=data.aviary_id,
        start_date=data.start_date,
        end_date=data.end_date,
        status="pending",
        total_price=total_price,
        services=services_json
    )
    db.add(booking_request)
    try:
        db.commit()
        db.refresh(booking_request)

        # return plain dict to avoid potential SQLAlchemy -> Pydantic conversion issues
        return {
            "id": booking_request.id,
            "pet_name": booking_request.pet_name,
            "species": booking_request.species,
            "owner_name": booking_request.owner_name,
            "owner_phone": booking_request.owner_phone,
            "description": booking_request.description,
            "aviary_id": booking_request.aviary_id,
            "start_date": booking_request.start_date,
            "end_date": booking_request.end_date,
            "status": booking_request.status,
            "total_price": booking_request.total_price,
            "created_at": booking_request.created_at,
            "services": booking_request.services
        }
    except Exception as e:
        db.rollback()
        # log the exception server-side and raise a clear HTTP error
        print('Error creating booking request:', e)
        raise HTTPException(status_code=500, detail='Не вдалося створити заявку на бронювання')


@app.get("/booking-requests", response_model=List[schemas.BookingRequestResponse])
def get_booking_requests(db: Session = Depends(get_db)):
    """Отримує усі заявки на бронювання (для модерування персоналом)"""
    return db.query(models.BookingRequest).order_by(models.BookingRequest.created_at.desc()).all()


@app.get("/booking-requests/pending", response_model=List[schemas.BookingRequestResponse])
def get_pending_booking_requests(db: Session = Depends(get_db)):
    """Отримує лише невідповідні (pending) заявки"""
    return db.query(models.BookingRequest).filter(models.BookingRequest.status == "pending").order_by(models.BookingRequest.created_at.desc()).all()


@app.put("/booking-requests/{id}", response_model=schemas.BookingRequestResponse)
def update_booking_request(id: int, data: schemas.BookingRequestCreate, db: Session = Depends(get_db)):
    """Редагує заявку на бронювання перед одобренням (тільки для pending статусу)"""
    db.expire_on_commit = False
    
    request = db.query(models.BookingRequest).filter(models.BookingRequest.id == id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")
    
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Можна редагувати тільки невідповідні заявки")
    
    # Перевіряємо наявність вольєра
    aviary = db.query(models.Aviary).filter(models.Aviary.id == data.aviary_id).first()
    if not aviary:
        raise HTTPException(status_code=404, detail="Вольєр не знайдено")
    
    # Розраховуємо нову ціну
    hotel_settings = db.query(models.HotelSettings).filter(models.HotelSettings.id == 1).first()
    billing_mode = hotel_settings.billing_mode if hotel_settings else "nights"
    
    days = (data.end_date - data.start_date).days
    if billing_mode == "days":
        days += 1
    if days <= 0:
        days = 1
    
    total_price = aviary.daily_price * days
    
    # Додаємо ціну послуг
    services_json = ""
    if data.service_ids:
        services = db.query(models.Service).filter(models.Service.id.in_(data.service_ids)).all()
        for s in services:
            total_price += s.price
        services_json = ",".join(str(s) for s in data.service_ids)
    
    # Оновлюємо дані заявки
    request.pet_name = data.pet_name
    request.species = data.species
    request.owner_name = data.owner_name
    request.owner_phone = data.owner_phone
    request.description = data.description
    request.aviary_id = data.aviary_id
    request.start_date = data.start_date
    request.end_date = data.end_date
    request.total_price = total_price
    request.services = services_json
    
    db.commit()
    db.refresh(request)
    return request


@app.patch("/booking-requests/{id}/approve", response_model=schemas.BookingResponse)
def approve_booking_request(id: int, db: Session = Depends(get_db)):
    """Одобрює заявку на бронювання і створює реальне бронювання"""
    db.expire_on_commit = False
    
    request = db.query(models.BookingRequest).filter(models.BookingRequest.id == id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")
    
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Цю заявку вже було оброблено")
    
    # Перевіряємо, чи вольєр все ще вільний
    conflict = db.query(models.Booking).filter(
        models.Booking.aviary_id == request.aviary_id,
        models.Booking.status != "Скасоване",
        models.Booking.start_date <= request.end_date,
        models.Booking.end_date >= request.start_date
    ).first()
    
    if conflict:
        request.status = "rejected"
        db.commit()
        raise HTTPException(status_code=400, detail="Вольєр вже зайнятий на обрані дати")
    
    # Створюємо тварину
    pet = models.HotelPet(
        name=request.pet_name,
        species=request.species,
        owner_name=request.owner_name,
        owner_phone=request.owner_phone,
        description=request.description
    )
    db.add(pet)
    db.flush()
    
    # Створюємо бронювання
    booking = models.Booking(
        pet_id=pet.id,
        aviary_id=request.aviary_id,
        start_date=request.start_date,
        end_date=request.end_date,
        status="Актуальне",
        total_price=request.total_price,
        payment_status="Не оплачено"
    )
    db.add(booking)
    db.flush()
    
    # Прив'язуємо послуги, якщо вони є
    if request.services:
        service_ids = [int(s) for s in request.services.split(",")]
        for service_id in service_ids:
            link = models.BookingServiceLink(booking_id=booking.id, service_id=service_id)
            db.add(link)
    
    # Оновлюємо статус заявки
    request.status = "approved"
    
    db.commit()
    db.refresh(booking)
    return booking


@app.patch("/booking-requests/{id}/reject")
def reject_booking_request(id: int, db: Session = Depends(get_db)):
    """Відхиляє заявку на бронювання"""
    db.expire_on_commit = False
    
    request = db.query(models.BookingRequest).filter(models.BookingRequest.id == id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Заявку не знайдено")
    
    if request.status != "pending":
        raise HTTPException(status_code=400, detail="Цю заявку вже було оброблено")
    
    request.status = "rejected"
    db.commit()
    return {"message": "Заявку відхилено"}