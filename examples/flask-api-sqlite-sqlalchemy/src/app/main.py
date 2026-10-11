"""Todo JSON API with Flask, SQLite storage, and plain SQLAlchemy ORM."""

from pathlib import Path

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base, Todo

# Example dir = src/app/main.py -> parents[2]; independent of cwd since the
# run command executes from the repo root.
DEFAULT_DB_FILE = Path(__file__).resolve().parents[2] / "todos.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_FILE}"


def _to_json(todo: Todo) -> dict:
    return {"id": todo.id, "title": todo.title, "done": todo.done}


def _valid_title(value: object) -> bool:
    return isinstance(value, str) and len(value) > 0


def create_app(db_url: str | None = None) -> Flask:
    db_url = db_url or DEFAULT_DB_URL
    if db_url == "sqlite:///:memory:":
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    elif db_url.startswith("sqlite:"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    sessions = sessionmaker(bind=engine, expire_on_commit=False)

    app = Flask(__name__)

    @app.get("/todos")
    def list_todos():
        with sessions() as session:
            todos = session.scalars(select(Todo).order_by(Todo.id)).all()
            return jsonify([_to_json(todo) for todo in todos])

    @app.post("/todos")
    def create_todo():
        body = request.get_json(silent=True, cache=False) or {}
        title = body.get("title")
        if not _valid_title(title):
            return jsonify({"error": "title must be a non-empty string"}), 422
        with sessions() as session:
            todo = Todo(title=title, done=False)
            session.add(todo)
            session.commit()
            return jsonify(_to_json(todo)), 201

    @app.get("/todos/<int:todo_id>")
    def get_todo(todo_id: int):
        with sessions() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return jsonify({"error": "Todo not found"}), 404
            return jsonify(_to_json(todo))

    @app.patch("/todos/<int:todo_id>")
    def update_todo(todo_id: int):
        body = request.get_json(silent=True, cache=False) or {}
        title = body.get("title")
        done = body.get("done")
        if title is not None and not _valid_title(title):
            return jsonify({"error": "title must be a non-empty string"}), 422
        with sessions() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return jsonify({"error": "Todo not found"}), 404
            if title is not None:
                todo.title = title
            if done is not None:
                todo.done = done
            session.commit()
            return jsonify(_to_json(todo))

    @app.delete("/todos/<int:todo_id>")
    def delete_todo(todo_id: int):
        with sessions() as session:
            todo = session.get(Todo, todo_id)
            if todo is None:
                return jsonify({"error": "Todo not found"}), 404
            session.delete(todo)
            session.commit()
        return "", 204

    return app


app = create_app()


def main() -> None:
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
