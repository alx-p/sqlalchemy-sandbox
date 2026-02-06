import os
from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Todo

app = Flask(__name__)

# Получение конфигурации из переменных окружения
DB_HOST = os.getenv('DB_HOST', 'postgres')  # Используем имя сервиса из docker-compose
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'mydatabase')
DB_USER = os.getenv('DB_USER', 'myuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'mypassword')

# Создание строки подключения
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создание движка SQLAlchemy (перемещаем выше)
engine = create_engine(DATABASE_URL)

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

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = session.query(Todo).all()
    return jsonify([{
        'id': todo.id,
        'user_id': todo.user_id,
        'title': todo.title,
        'completed': todo.completed,
        'created_at': todo.created_at.isoformat() if todo.created_at else None,
        'updated_at': todo.updated_at.isoformat() if todo.updated_at else None
    } for todo in todos])

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    new_todo = Todo(
        user_id=data['user_id'],
        title=data['title'],
        completed=data.get('completed', False)
    )
    session.add(new_todo)
    session.commit()
    return jsonify({
        'id': new_todo.id,
        'user_id': new_todo.user_id,
        'title': new_todo.title,
        'completed': new_todo.completed
    }), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = session.query(Todo).get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    data = request.get_json()
    todo.title = data.get('title', todo.title)
    todo.completed = data.get('completed', todo.completed)
    session.commit()

    return jsonify({
        'id': todo.id,
        'user_id': todo.user_id,
        'title': todo.title,
        'completed': todo.completed
    })

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = session.query(Todo).get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    session.delete(todo)
    session.commit()
    return jsonify({'message': 'Todo deleted successfully'})

if __name__ == '__main__':
    # Инициализируем базу данных перед запуском сервера
    if not init_db():
        print("Failed to initialize database. Exiting...")
        exit(1)

    app.run(host='0.0.0.0', port=5000)