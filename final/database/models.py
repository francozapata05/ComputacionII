from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB # Importamos JSONB para PostgreSQL
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey

# Instancia de SQLAlchemy, inicializada posteriormente en app.py
db = SQLAlchemy()

# --- Modelos de Datos ---

class User(db.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True, nullable=False)
    password = Column(String(255), nullable=False) # Usamos 255 para almacenar hashes seguros en producción
    # Relación uno-a-muchos con las Searches. El backref es 'user'
    search_history = db.relationship('Search', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'

class Search(db.Model):
    __tablename__ = 'search'
    id = Column(Integer, primary_key=True)
    task_id = Column(String(36), unique=True, nullable=False)
    url = Column(String(500), nullable=False)
    
    # Información de rendimiento y scrapping
    status = Column(String(20), nullable=False) # pending, done, error
    title = Column(String(200), nullable=True)
    description = Column(String(500), nullable=True)
    loading_time = Column(Float, nullable=True)
    hosting_company = Column(JSONB, nullable=True)
    
    # Para almacenar el resto (DNS, nameservers, registro de dominio completo)
    details = Column(JSONB, nullable=True) 
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Clave Foránea: referencia a la tabla 'user'
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Search {self.url} (Status: {self.status})>'