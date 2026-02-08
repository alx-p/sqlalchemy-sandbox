from flask import Flask, jsonify, request
# from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload # sessionmaker, 
from models import User, Todo
from database import SessionLocal, Base, engine, init_db

app = Flask(__name__)

# Создаем все таблицы
Base.metadata.create_all(bind=engine)

# Создание движка SQLAlchemy (перемещаем выше)
#engine = create_engine(DATABASE_URL)

# Создание сессии
#Session = sessionmaker(bind=engine)
session = SessionLocal()

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

@app.route('/todos_u', methods=['GET'])
def get_todos_u():
    # Загружаем задачи с их владельцами (users) в одном запросе
    todos = session.query(Todo).options(joinedload(Todo.owner)).all()

    result = []
    for todo in todos:
        result.append({
            "id": todo.id,
            "title": todo.title,
            "description": todo.description,
            "completed": todo.completed,
            "created_at": todo.created_at.isoformat(),
            "updated_at": todo.updated_at.isoformat(),
            "user": {
                "id": todo.owner.id,
                "username": todo.owner.username,
                "email": todo.owner.email,
                "full_name": todo.owner.full_name
            }
        })
    return jsonify(result)

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

# создание пользователя
@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    new_user = User(
        username=data['username'],
        email=data['email'],
        full_name=data.get('full_name', ''),
        is_active=data.get('is_active', True)
    )

    session.add(new_user)
    session.commit()

    return jsonify({
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "full_name": new_user.full_name,
        "is_active": new_user.is_active
    }), 201

@app.route('/todos_u', methods=['POST'])
def create_todo_u():
    data = request.get_json()

    # Создаем новую задачу
    new_todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        completed=data.get('completed', False),
        user_id=data['user_id']  # ID пользователя, который создает задачу
    )

    session.add(new_todo)
    session.commit()

    # Возвращаем созданную задачу с информацией о пользователе
    todo_with_user = session.query(Todo).options(joinedload(Todo.owner)).filter(Todo.id == new_todo.id).first()

    return jsonify({
        "id": todo_with_user.id,
        "title": todo_with_user.title,
        "description": todo_with_user.description,
        "completed": todo_with_user.completed,
        "created_at": todo_with_user.created_at.isoformat(),
        "updated_at": todo_with_user.updated_at.isoformat(),
        "user": {
            "id": todo_with_user.owner.id,
            "username": todo_with_user.owner.username,
            "email": todo_with_user.owner.email,
            "full_name": todo_with_user.owner.full_name
        }
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