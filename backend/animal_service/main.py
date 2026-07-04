import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Header, status, File, UploadFile, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
import cloudinary
import cloudinary.uploader
import models, schemas
from database import SessionLocal
from jose import jwt
import uuid

app = FastAPI(title="PetCloud Animal Service")

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8001/login")


def get_token_payload(token: str = Depends(oauth2_scheme)):
    """Просто розшифровує токен і повертає його дані"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Невірний токен")

def require_admin(payload: dict = Depends(get_token_payload)):
    """Перевіряє, чи є користувач адміністратором"""
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Ця дія дозволена лише адміністраторам"
        )
    return payload


# Функція для отримання схеми з токена
def get_tenant_schema(token: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    print(f"DEBUG: Received token: {token.credentials}")
    try:
        # HTTPBearer автоматично відріже слово "Bearer" і дасть тобі чистий токен
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        schema_name = payload.get("schema_name")
        if not schema_name:
            raise HTTPException(status_code=401, detail="No schema in token")
        return schema_name
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Залежність для отримання БД з потрібним search_path
def get_db_with_schema(schema_name: str = Depends(get_tenant_schema)):
    db = SessionLocal()
    try:
        # Встановлюємо шлях пошуку для поточного сеансу
        db.execute(text(f'SET search_path TO "{schema_name}"'))
        yield db
    finally:
        db.close()


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


def get_public_db(schema_name: str = Query(..., min_length=1)):
    db = SessionLocal()
    try:
        db.execute(text(f'SET search_path TO "{schema_name}"'))
        yield db
    finally:
        db.close()


@app.get("/public/settings", response_model=schemas.SiteSettingsResponse)
def get_public_settings(schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    settings = db.query(models.SiteSettings).filter(models.SiteSettings.id == 1).first()
    if not settings:
        settings = models.SiteSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@app.get("/public/animals", response_model=List[schemas.AnimalResponse])
def get_public_animals(schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    return db.query(models.ShelterAnimal).filter(models.ShelterAnimal.is_public == True).all()


@app.get("/public/site", response_model=schemas.PublicSiteResponse)
def get_public_site(schema_name: str = Query(..., min_length=1), db: Session = Depends(get_public_db)):
    settings = db.query(models.SiteSettings).filter(models.SiteSettings.id == 1).first()
    if not settings:
        settings = models.SiteSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    animals = db.query(models.ShelterAnimal).filter(models.ShelterAnimal.is_public == True).all()
    return {
        "settings": settings,
        "animals": animals
    }


@app.post("/animals/upload", response_model=schemas.ImageUploadResponse)
async def upload_animal_image(file: UploadFile = File(...), _admin: dict = Depends(require_admin)):
    result = upload_image_to_cloudinary(file, folder="petcloud/shelter")
    return {"url": result["secure_url"], "public_id": result["public_id"]}


@app.get("/settings", response_model=schemas.SiteSettingsResponse)
def get_settings(_admin: dict = Depends(require_admin), db: Session = Depends(get_db_with_schema)):
    settings = db.query(models.SiteSettings).filter(models.SiteSettings.id == 1).first()
    if not settings:
        settings = models.SiteSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@app.put("/settings", response_model=schemas.SiteSettingsResponse)
def update_settings(data: schemas.SiteSettingsUpdate, _admin: dict = Depends(require_admin), db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False
    settings = db.query(models.SiteSettings).filter(models.SiteSettings.id == 1).first()
    if not settings:
        settings = models.SiteSettings(id=1)
        db.add(settings)
        db.commit()
        db.refresh(settings)

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


@app.post("/settings/upload", response_model=schemas.ImageUploadResponse)
async def upload_settings_image(file: UploadFile = File(...), _admin: dict = Depends(require_admin)):
    result = upload_image_to_cloudinary(file, folder="petcloud/shelter/settings")
    return {"url": result["secure_url"], "public_id": result["public_id"]}


@app.get("/animals", response_model=List[schemas.AnimalResponse])
def get_animals(db: Session = Depends(get_db_with_schema)):
    # SQLAlchemy тепер автоматично шукатиме в tenant_X
    return db.query(models.ShelterAnimal).all()

@app.post("/animals", response_model=schemas.AnimalResponse)
def create_animal(animal: schemas.AnimalCreate, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    new_animal = models.ShelterAnimal(
        name=animal.name,
        age=animal.age,
        species=animal.species,
        description=animal.description,
        photo_url=animal.photo_url,
        health_status=animal.health_status,
        is_public=animal.is_public or False
    )
    
    db.add(new_animal)
    db.flush()
    db.refresh(new_animal)
    db.commit()
    return new_animal

@app.put("/animals/{animal_id}", response_model=schemas.AnimalResponse)
def update_animal(animal_id: int, updated_data: schemas.AnimalCreate, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    db_animal = db.query(models.ShelterAnimal).filter(models.ShelterAnimal.id == animal_id).first()
    
    if not db_animal:
        raise HTTPException(status_code=404, detail="Тварину не знайдено")

    # Оновлюємо поля
    for key, value in updated_data.model_dump().items():
        setattr(db_animal, key, value)

    db.flush()
    db.refresh(db_animal)
    db.commit()
    return db_animal

@app.delete("/animals/{animal_id}")
def delete_animal(animal_id: int, _admin: dict = Depends(require_admin), db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    db_animal = db.query(models.ShelterAnimal).filter(models.ShelterAnimal.id == animal_id).first()
    
    if not db_animal:
        raise HTTPException(status_code=404, detail="Тварину не знайдено")
    
    db.delete(db_animal)
    db.commit()
    return {"message": "Тварину успішно видалено"}

@app.get("/medical-records")
def get_medical_records(db: Session = Depends(get_db_with_schema)):
    results = db.query(
        models.MedicalRecord, 
        models.ShelterAnimal.name
    ).join(models.ShelterAnimal).all()

    formatted_results = []
    for record, animal_name in results:
        record_data = {
            "id": record.id,
            "animal_id": record.animal_id,
            "record_date": record.record_date,
            "type": record.type,
            "notes": record.notes,
            "animal_name": animal_name
        }
        formatted_results.append(record_data)

    return formatted_results

@app.post("/medical-records")
def create_medical_record(record: schemas.MedicalRecordCreate, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    db_record = models.MedicalRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.put("/medical-records/{record_id}")
def update_medical_record(record_id: int, record_update: schemas.MedicalRecordUpdate, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    db_record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    for key, value in record_update.model_dump(exclude_unset=True).items():
        setattr(db_record, key, value)
    
    db.commit()
    db.refresh(db_record)
    return db_record

@app.delete("/medical-records/{record_id}")
def delete_medical_record(record_id: int, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False
    
    db_record = db.query(models.MedicalRecord).filter(models.MedicalRecord.id == record_id).first()
    if not db_record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    db.delete(db_record)
    db.commit()
    return {"message": "Record deleted successfully"}

# --- SHELTER TASKS ENDPOINTS ---
@app.get("/tasks", response_model=List[schemas.ShelterTaskResponse])
def get_tasks(db: Session = Depends(get_db_with_schema)):
    tasks = db.query(models.ShelterTask).all()
    result = []
    for task in tasks:
        task_data = {
            "id": task.id,
            "title": task.title,
            "date_time": task.date_time,
            "is_completed": task.is_completed,
            "animal_id": task.animal_id,
            "animal_name": None,
            "recurrence_group_id": task.recurrence_group_id,
            "repeat_days": None
        }
        if task.animal_id:
            animal = db.query(models.ShelterAnimal).filter(models.ShelterAnimal.id == task.animal_id).first()
            if animal:
                task_data["animal_name"] = animal.name
        result.append(task_data)
    return result

@app.get("/tasks/due_soon", response_model=List[schemas.ShelterTaskResponse])
def get_due_soon_tasks(db: Session = Depends(get_db_with_schema)):
    now = datetime.utcnow()
    soon = now + timedelta(hours=24)
    tasks = db.query(models.ShelterTask).filter(
        models.ShelterTask.is_completed == False,
        models.ShelterTask.date_time <= soon
    ).order_by(models.ShelterTask.date_time.asc()).all()

    result = []
    for task in tasks:
        task_data = {
            "id": task.id,
            "title": task.title,
            "date_time": task.date_time,
            "is_completed": task.is_completed,
            "animal_id": task.animal_id,
            "animal_name": None,
            "recurrence_group_id": task.recurrence_group_id,
            "repeat_days": None
        }
        if task.animal_id:
            animal = db.query(models.ShelterAnimal).filter(models.ShelterAnimal.id == task.animal_id).first()
            if animal:
                task_data["animal_name"] = animal.name
        result.append(task_data)
    return result

@app.post("/tasks", response_model=schemas.ShelterTaskResponse)
def create_task(task: schemas.ShelterTaskCreate, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False
    
    # Якщо передано recurrence_group_id - використовуємо його, інакше генеруємо новий
    group_id = task.recurrence_group_id or str(uuid.uuid4())
    repeat_days = task.repeat_days or 1
    
    if repeat_days <= 1:
        # Завдання без повтору
        db_task = models.ShelterTask(
            title=task.title,
            date_time=task.date_time,
            animal_id=task.animal_id,
            is_completed=False,
            recurrence_group_id=task.recurrence_group_id if task.recurrence_group_id else None
        )
        db.add(db_task)
        db.flush()
        db.refresh(db_task)
        db.commit()
        return db_task
    
    # Створюємо кілька завдань для повтору
    first_task = None
    for i in range(repeat_days):
        next_date = task.date_time + timedelta(days=i)
        
        db_task = models.ShelterTask(
            title=task.title,
            date_time=next_date,
            animal_id=task.animal_id,
            is_completed=False,
            recurrence_group_id=group_id
        )
        db.add(db_task)
        db.flush()
        
        if i == 0:
            first_task = db_task

    db.commit()
    db.refresh(first_task)
    return first_task

@app.put("/tasks/{task_id}", response_model=schemas.ShelterTaskResponse)
def update_task(task_id: int, task_update: schemas.ShelterTaskUpdate, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    db_task = db.query(models.ShelterTask).filter(models.ShelterTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    for key, value in task_update.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    
    db.flush()
    db.refresh(db_task)
    
    task_data = {
        "id": db_task.id,
        "title": db_task.title,
        "date_time": db_task.date_time,
        "is_completed": db_task.is_completed,
        "animal_id": db_task.animal_id,
        "animal_name": None
    }
    if db_task.animal_id:
        animal = db.query(models.ShelterAnimal).filter(models.ShelterAnimal.id == db_task.animal_id).first()
        if animal:
            task_data["animal_name"] = animal.name
    db.commit()
    return task_data

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, _admin: dict = Depends(require_admin), db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    db_task = db.query(models.ShelterTask).filter(models.ShelterTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@app.delete("/tasks/{task_id}/recurrence")
def cancel_task_recurrence_from_day(task_id: int, _admin: dict = Depends(require_admin), db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    current_task = db.query(models.ShelterTask).filter(models.ShelterTask.id == task_id).first()
    if not current_task:
        raise HTTPException(status_code=404, detail="Завдання не знайдено")
    
    if not current_task.recurrence_group_id:
        raise HTTPException(status_code=400, detail="Це завдання не є частиною серії повторень")
    
    # 2. Видаляємо завдання цієї ж групи, у яких дата/час рівні або більші за поточне
    deleted_count = db.query(models.ShelterTask).filter(
        models.ShelterTask.recurrence_group_id == current_task.recurrence_group_id,
        models.ShelterTask.date_time >= current_task.date_time
    ).delete(synchronize_session=False)
    
    db.commit()
    return {"message": f"Повторення скасовано з цього дня. Видалено майбутніх завдань: {deleted_count}"}

#INVENTORY ENDPOINTS

@app.get("/inventory", response_model=List[schemas.ShelterInventoryResponse])
def get_inventory(db: Session = Depends(get_db_with_schema)):
    inventory = db.query(models.ShelterInventory).all()
    return inventory

@app.post("/inventory", response_model=schemas.ShelterInventoryResponse)
def create_inventory_item(item: schemas.ShelterInventoryCreate, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    db_item = models.ShelterInventory(
        name=item.name,
        category=item.category,
        quantity=item.quantity,
        target_quantity=item.target_quantity,
        target_animal=item.target_animal,
        unit=item.unit
    )

    db.add(db_item)
    db.flush()
    db.refresh(db_item)
    db.commit()
    return db_item

@app.put("/inventory/{item_id}", response_model=schemas.ShelterInventoryResponse)
def update_inventory_item(item_id: int, item_update: schemas.ShelterInventoryUpdate, db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False

    db_item = db.query(models.ShelterInventory).filter(models.ShelterInventory.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Товар не знайдено на складі")
    
    for key, value in item_update.model_dump(exclude_unset=True).items():
        setattr(db_item, key, value)
        
    db.flush()
    db.refresh(db_item)
    db.commit()
    return db_item

@app.delete("/inventory/{item_id}")
def delete_inventory_item(item_id: int, _admin: dict = Depends(require_admin), db: Session = Depends(get_db_with_schema)):
    db.expire_on_commit = False
    
    db_item = db.query(models.ShelterInventory).filter(models.ShelterInventory.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Товар не знайдено на складі")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Товар успішно видалено зі складу"}