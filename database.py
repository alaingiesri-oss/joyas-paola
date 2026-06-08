import os
import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, desc
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# Configurar URL de la Base de Datos
# Por defecto usa SQLite local, pero si encuentra DATABASE_URL (ej. en Streamlit Secrets o Variables de Entorno)
# usa esa conexión PostgreSQL en la nube.
DB_URL = "sqlite:///inventory.db"

# Intentar obtener de variables de entorno o secretos de Streamlit
env_url = os.environ.get("DATABASE_URL")
try:
    if not env_url:
        env_url = st.secrets.get("DATABASE_URL")
except Exception:
    pass

if env_url:
    # SQLAlchemy requiere que las URLs comiencen con postgresql:// en vez de postgres://
    if env_url.startswith("postgres://"):
        DB_URL = env_url.replace("postgres://", "postgresql://", 1)
    else:
        DB_URL = env_url

# Crear el motor de base de datos
engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Definición del modelo de datos de la Joya
class Jewelry(Base):
    __tablename__ = "jewelry"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String)
    material = Column(String)
    price = Column(Float, nullable=False)
    description = Column(Text)
    image_path = Column(Text) # Puede ser una ruta local o una cadena Base64
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)
    value = Column(Text, nullable=False)

def init_db():
    """Inicializa la base de datos y crea la tabla si no existe."""
    Base.metadata.create_all(bind=engine)

def get_setting(key, default_value=None):
    """Obtiene el valor de una configuración por su clave."""
    session = SessionLocal()
    try:
        setting = session.query(Setting).filter(Setting.key == key).first()
        if setting:
            return setting.value
        return default_value
    except Exception:
        return default_value
    finally:
        session.close()

def set_setting(key, value):
    """Guarda o actualiza una configuración de la tienda."""
    session = SessionLocal()
    try:
        setting = session.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = str(value)
        else:
            new_setting = Setting(key=key, value=str(value))
            session.add(new_setting)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error al guardar configuración: {e}")
    finally:
        session.close()

def add_item(name, category, material, price, description, image_path):
    """Agrega una nueva joya a la base de datos."""
    session = SessionLocal()
    try:
        new_item = Jewelry(
            name=name,
            category=category,
            material=material,
            price=price,
            description=description,
            image_path=image_path
        )
        session.add(new_item)
        session.commit()
        new_id = new_item.id
        return new_id
    finally:
        session.close()

def get_all_items():
    """Retorna todas las joyas registradas."""
    session = SessionLocal()
    try:
        items = session.query(Jewelry).order_by(desc(Jewelry.created_at)).all()
        # Convertir a lista de diccionarios para mantener compatibilidad
        result = []
        for item in items:
            result.append({
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "material": item.material,
                "price": item.price,
                "description": item.description,
                "image_path": item.image_path,
                "created_at": item.created_at
            })
        return result
    finally:
        session.close()

def get_item(item_id):
    """Retorna una joya específica por su ID."""
    session = SessionLocal()
    try:
        item = session.query(Jewelry).filter(Jewelry.id == item_id).first()
        if item:
            return {
                "id": item.id,
                "name": item.name,
                "category": item.category,
                "material": item.material,
                "price": item.price,
                "description": item.description,
                "image_path": item.image_path,
                "created_at": item.created_at
            }
        return None
    finally:
        session.close()

def update_item(item_id, name, category, material, price, description, image_path):
    """Actualiza la información de una joya existente."""
    session = SessionLocal()
    try:
        item = session.query(Jewelry).filter(Jewelry.id == item_id).first()
        if item:
            item.name = name
            item.category = category
            item.material = material
            item.price = price
            item.description = description
            item.image_path = image_path
            session.commit()
    finally:
        session.close()

def delete_item(item_id):
    """Elimina una joya de la base de datos."""
    session = SessionLocal()
    try:
        item = session.query(Jewelry).filter(Jewelry.id == item_id).first()
        if item:
            session.delete(item)
            session.commit()
    finally:
        session.close()
