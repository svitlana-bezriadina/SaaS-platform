import re
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import models
import schemas
from database import engine, get_db, create_tenant_schema

public_tables = [models.Organization.__table__, models.User.__table__]
models.Base.metadata.create_all(bind=engine, tables=public_tables)

app = FastAPI(title="PetCloud Auth Service")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний токен")


def get_current_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if payload.get("role") != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Тільки для адміністраторів")

    user = db.query(models.User).filter(models.User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний користувач")
    return user

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    user = db.query(models.User).filter(models.User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний користувач")
    return user

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Налаштування для паролів та токенів
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "diploma_super_secret_key_change_me_later"
ALGORITHM = "HS256"

@app.post("/register")
def register_organization(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if data.org_type not in ["shelter", "hotel"]:
        raise HTTPException(status_code=400, detail="Невірний тип організації")

    # Перевіряємо, чи немає вже такої організації або юзера
    if db.query(models.Organization).filter(models.Organization.name == data.name).first():
        raise HTTPException(status_code=400, detail="Організація з такою назвою вже існує")
    if db.query(models.User).filter(models.User.email == data.admin_email).first():
        raise HTTPException(status_code=400, detail="Користувач з таким email вже існує")

    # Генеруємо унікальну назву схеми (наприклад, tenant_1, tenant_2)
    org_count = db.query(models.Organization).count()
    schema_name = f"tenant_{data.name.lower()}_{org_count + 1}"

    def slugify(value: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower())
        return cleaned.strip("-") or "org"

    desired_subdomain = (data.subdomain or data.name).strip().lower()
    desired_subdomain = slugify(desired_subdomain)
    subdomain = desired_subdomain
    suffix = 1
    while db.query(models.Organization).filter(models.Organization.subdomain == subdomain).first():
        suffix += 1
        subdomain = f"{desired_subdomain}-{suffix}"

    # 1. Зберігаємо організацію в public
    new_org = models.Organization(
        name=data.name,
        org_type=data.org_type,
        schema_name=schema_name,
        subdomain=subdomain
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)

    # 2. Зберігаємо користувача в public
    hashed_password = pwd_context.hash(data.password)
    new_user = models.User(
        organization_id=new_org.id,
        full_name=data.full_name,
        email=data.admin_email,
        password_hash=hashed_password,
        role="admin"
    )
    db.add(new_user)
    db.commit()

    # 3. МАГІЯ: Створюємо ізольовану базу (схему) для клієнта
    create_tenant_schema(schema_name, data.org_type)

    return {"message": f"Організацію успішно зареєстровано! Створено схему {schema_name}"}


@app.post("/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Шукаємо користувача
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not pwd_context.verify(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Невірний email або пароль")

    # Дістаємо його організацію, щоб знати тип та схему
    org = db.query(models.Organization).filter(models.Organization.id == user.organization_id).first()

    # Створюємо JWT Токен
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode = {
        "sub": user.email,
        "user_id": user.id,
        "user_name": user.full_name,
        "org_id": org.id,
        "org_type": org.org_type,
        "schema_name": org.schema_name, # НАЙВАЖЛИВІШЕ: передаємо ім'я схеми в токені!
        "role": user.role,
        "exp": expire
    }
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # Повертаємо дані, які потрібні нашому Vue (Pinia)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_name": user.full_name,
        "org_type": org.org_type,
        "role": user.role,
        "subdomain": org.subdomain
    }

@app.get("/auth/org", response_model=schemas.OrganizationPublicResponse)
def get_current_org(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Організацію не знайдено")
    return org

@app.put("/auth/org/subdomain", response_model=schemas.OrganizationPublicResponse)
def update_org_subdomain(data: schemas.SubdomainUpdate, current_user: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.id == current_user.organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Організацію не знайдено")

    def slugify(value: str) -> str:
        cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower())
        return cleaned.strip("-") or "org"

    desired_subdomain = data.subdomain.strip().lower()
    desired_subdomain = slugify(desired_subdomain)
    subdomain = desired_subdomain
    suffix = 1
    while db.query(models.Organization).filter(models.Organization.subdomain == subdomain).filter(models.Organization.id != org.id).first():
        suffix += 1
        subdomain = f"{desired_subdomain}-{suffix}"

    org.subdomain = subdomain
    db.commit()
    db.refresh(org)
    return org

@app.get("/org-info/{subdomain}")
def get_org_info(subdomain: str, db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.subdomain == subdomain).first()
    if not org:
        raise HTTPException(status_code=404, detail="Організацію не знайдено")
    return org

@app.post("/auth/workers", response_model=schemas.WorkerResponse)
def create_worker(data: schemas.WorkerCreate, current_user: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    # ... перевірка email ...
    new_worker = models.User(
        organization_id=current_user.organization_id,
        full_name=data.full_name,
        email=data.email,
        phone_number=data.phone_number, # <--- Зберігаємо телефон
        password_hash=pwd_context.hash(data.password),
        role="worker"
    )
    db.add(new_worker)
    db.commit()
    db.refresh(new_worker)
    return new_worker

@app.get("/auth/workers", response_model=List[schemas.WorkerResponse])
def list_workers(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    workers = db.query(models.User).filter(
        models.User.organization_id == current_user.organization_id
    ).all()
    return workers

@app.delete("/auth/workers/{worker_id}")
def delete_worker(worker_id: int, current_user: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    worker = db.query(models.User).filter(
        models.User.id == worker_id,
        models.User.organization_id == current_user.organization_id
    ).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Працівник не знайдений")
    if worker.role == "admin":
        raise HTTPException(status_code=400, detail="Неможливо видалити адміністратора")
    
    db.delete(worker)
    db.commit()
    return {"message": "Працівник успішно видалений"}

@app.put("/auth/workers/{worker_id}", response_model=schemas.WorkerResponse)
def update_worker(worker_id: int, data: schemas.WorkerCreate, current_user: models.User = Depends(get_current_admin_user), db: Session = Depends(get_db)):
    worker = db.query(models.User).filter(
        models.User.id == worker_id,
        models.User.organization_id == current_user.organization_id
    ).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Працівник не знайдений")
    if worker.role == "admin":
        raise HTTPException(status_code=400, detail="Неможливо редагувати адміністратора")
    
    worker.full_name = data.full_name
    worker.email = data.email
    worker.phone_number = data.phone_number
    if data.password:
        worker.password_hash = pwd_context.hash(data.password)
    
    db.commit()
    db.refresh(worker)
    return worker