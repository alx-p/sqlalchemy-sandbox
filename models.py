from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base # Абсолютный импорт

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)

    # Связь с todos (один пользователь может иметь много задач)
    todos = relationship("Todo", back_populates="owner")

class Todo(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(String(200))
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Внешний ключ, ссылающийся на пользователя
    user_id = Column(Integer, ForeignKey('users.id'))

    # Связь с пользователем (одна задача принадлежит одному пользователю)
    owner = relationship("User", back_populates="todos")