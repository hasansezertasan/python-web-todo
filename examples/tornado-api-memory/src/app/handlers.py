"""Tornado request handlers for the todo JSON API."""

import json

import tornado.web

from .store import TodoStore, todo_to_dict


class BaseHandler(tornado.web.RequestHandler):
    @property
    def store(self) -> TodoStore:
        return self.application.settings["store"]

    def parse_json_body(self) -> dict | None:
        """Parse the request body as a JSON object.

        Returns the object, or writes a 422 JSON error and returns None.
        An empty body is treated as an empty object.
        """
        raw = self.request.body.decode("utf-8") if self.request.body else ""
        if not raw.strip():
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self.set_status(422)
            self.write({"detail": "Request body must be valid JSON"})
            return None
        if not isinstance(data, dict):
            self.set_status(422)
            self.write({"detail": "Request body must be a JSON object"})
            return None
        return data

    def write_not_found(self) -> None:
        self.set_status(404)
        self.write({"detail": "Todo not found"})


class TodoListHandler(BaseHandler):
    def get(self) -> None:
        self.set_header("Content-Type", "application/json")
        self.finish(json.dumps([todo_to_dict(t) for t in self.store.list()]))

    def post(self) -> None:
        data = self.parse_json_body()
        if data is None:
            return
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            self.set_status(422)
            self.write({"detail": "Title must be a non-empty string"})
            return
        todo = self.store.create(title=title)
        self.set_status(201)
        self.write(todo_to_dict(todo))


class TodoDetailHandler(BaseHandler):
    def get(self, todo_id: str) -> None:
        todo = self.store.get(int(todo_id))
        if todo is None:
            self.write_not_found()
            return
        self.write(todo_to_dict(todo))

    def patch(self, todo_id: str) -> None:
        todo = self.store.get(int(todo_id))
        if todo is None:
            self.write_not_found()
            return
        data = self.parse_json_body()
        if data is None:
            return
        title = data.get("title", None)
        if "title" in data and (not isinstance(title, str) or not title.strip()):
            self.set_status(422)
            self.write({"detail": "Title must be a non-empty string"})
            return
        done = data.get("done", None)
        if "done" in data and not isinstance(done, bool):
            self.set_status(422)
            self.write({"detail": "Done must be a boolean"})
            return
        updated = self.store.update(int(todo_id), title=title, done=done)
        if updated is None:
            self.write_not_found()
            return
        self.write(todo_to_dict(updated))

    def delete(self, todo_id: str) -> None:
        if not self.store.delete(int(todo_id)):
            self.write_not_found()
            return
        self.set_status(204)
        self.finish()
