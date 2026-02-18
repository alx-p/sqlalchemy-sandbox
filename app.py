from flask import Flask, jsonify, request
from sqlalchemy.orm import joinedload # sessionmaker, 
from models import Airplane
from database import SessionLocal, Base, engine, init_db

app = Flask(__name__)

#Session = sessionmaker(bind=engine)
session = SessionLocal()

if __name__ == '__main__':
    # Инициализируем базу данных перед запуском сервера
    if not init_db():
        print("Failed to initialize database. Exiting...")
        exit(1)

    app.run(host='0.0.0.0', port=5000)