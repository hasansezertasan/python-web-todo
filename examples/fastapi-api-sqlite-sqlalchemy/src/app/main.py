"""Todo JSON API with FastAPI and SQLite storage via SQLAlchemy."""

from collections.abc import Iterator
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base, Todo
from .repository import SqlAlchemyTodoRepository
from .schemas import TodoCreate, TodoRead, TodoUpdate

DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "todos.db"
DEFAULT_DB_URL = f"sqlite:///{DEFAULT_DB_PATH}"


def create_app(db_url: str | None = None) -> FastAPI:
    db_url = db_url or DEFAULT_DB_URL
    connect_args = {"check_same_thread": False}
    if db_url.endswith(":memory:"):
        engine = create_engine(db_url, connect_args=connect_args, poolclass=StaticPool)
    else:
        engine = create_engine(db_url, connect_args=connect_args)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)

    def get_db() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    app = FastAPI(title="Todo API (FastAPI, SQLite + SQLAlchemy)")

    @app.get("/todos", response_model=list[TodoRead])
    def list_todos(db: Session = Depends(get_db)) -> list[Todo]:
        return SqlAlchemyTodoRepository(db).list()

    @app.post("/todos", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
    def create_todo(payload: TodoCreate, db: Session = Depends(get_db)) -> Todo:
        return SqlAlchemyTodoRepository(db).create(title=payload.title)

    @app.get("/todos/{todo_id}", response_model=TodoRead)
    def get_todo(todo_id: int, db: Session = Depends(get_db)) -> Todo:
        try:
            return SqlAlchemyTodoRepository(db).get(todo_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Todo not found") from None

    @app.patch("/todos/{todo_id}", response_model=TodoRead)
    def update_todo(
        todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)
    ) -> Todo:
        try:
            return SqlAlchemyTodoRepository(db).update(
                todo_id, title=payload.title, done=payload.done
            )
        except KeyError:
            raise HTTPException(status_code=404, detail="Todo not found") from None

    @app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_todo(todo_id: int, db: Session = Depends(get_db)) -> Response:
        try:
            SqlAlchemyTodoRepository(db).delete(todo_id)
        except KeyError:
            raise HTTPException(status_code=404, detail="Todo not found") from None
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
