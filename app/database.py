import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# --- LA CADENA REAL DE TU PANEL (Región us-east-2 y Puerto 6543) ---
DATABASE_URL = "postgresql://postgres.uwnejtbsyracpokxnsbx:ProyectoFinal01@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

# Forzamos la variable en el entorno para matar cualquier caché vieja en Windows
os.environ["SUPABASE_DB_URL"] = DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_pre_ping=True  # Obliga a verificar la conexión antes de lanzar las queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()