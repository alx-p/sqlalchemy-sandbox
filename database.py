import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import psycopg2
from psycopg2 import OperationalError

# Получение конфигурации из переменных окружения
DB_HOST = os.getenv('DB_HOST', 'postgres')  # Используем имя сервиса из docker-compose
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')
DB_USER = os.getenv('DB_USER', 'myuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mypassword')

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#SQLALCHEMY_DATABASE_URL = "postgresql://myuser:mypassword@postgres_db/mydatabase"

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Функция инициализации базы данных
def init_db():
    # Добавляем задержку для подстраховки
    #time.sleep(5)
    try:
        # Проверяем подключение
        with engine.connect() as conn:
            print("Successfully connected to the database")
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

    # Создаем таблицы только если их нет
    try:
        Base.metadata.create_all(engine)
        print("Tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def create_db_engine():
    max_retries = 10
    retry_delay = 2
    for i in range(max_retries):
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            # Проверяем подключение
            with engine.connect() as conn:
                pass
            return engine
        except OperationalError as e:
            if i == max_retries - 1:
                raise
            print(f"Attempt {i+1} failed. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
            retry_delay *= 2  # Экспоненциальное увеличение задержки

engine = create_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()