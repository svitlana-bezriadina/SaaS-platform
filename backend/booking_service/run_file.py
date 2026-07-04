from sqlalchemy import create_engine, text

DB_URL = "postgresql://admin:2321919458@localhost:5435/petcloud"
engine = create_engine(DB_URL)

with engine.begin() as conn:
    schema_name1 = "tenant_притулок_1"
    schema_name2 = "tenant_готель_2"
    


    # 2. Схема ПРИТУЛКУ
    conn.execute(text(f'SET search_path TO "{schema_name1}"'))
    
    conn.execute(text(f'ALTER TABLE "{schema_name1}".settings ALTER COLUMN contact_phone TYPE VARCHAR(255);'))
    print(f"✅")

    # 3. Схема ГОТЕЛЮ (об'єднали всі ALTER в один запит для оптимізації)
    conn.execute(text(f'SET search_path TO "{schema_name2}"'))
    conn.execute(text(f'ALTER TABLE "{schema_name2}".settings ALTER COLUMN contact_phone TYPE VARCHAR(255);'))
    conn.execute(text(f'ALTER TABLE "{schema_name2}".hotel_pets ALTER COLUMN owner_phone TYPE VARCHAR(255);'))
    conn.execute(text(f'ALTER TABLE "{schema_name2}".booking_requests ALTER COLUMN owner_phone TYPE VARCHAR(255);'))
    print("\n🎉")