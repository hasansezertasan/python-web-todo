# JSON API contract

Applies to all `*-api-*` examples.

## Endpoints

| Method | Path | Purpose | Success |
| ------ | ---- | ------- | ------- |
| `GET` | `/todos` | List all items | `200` + JSON array of items |
| `POST` | `/todos` | Create an item (`{"title": "..."}`) | `201` + created item |
| `GET` | `/todos/{id}` | Get one item | `200` + item, or `404` |
| `PATCH` | `/todos/{id}` | Update title and/or done | `200` + item, or `404` |
| `DELETE` | `/todos/{id}` | Delete an item | `204`, or `404` |

Field names follow `todo-behavior.md`: `id`, `title`, `done`.

## Errors

- Missing/empty title: `422` with a JSON body describing the problem.
- Unknown id: `404` with a JSON body describing the problem.
- Exact error shapes stay idiomatic per framework; contract tests assert status codes and that a JSON body is present, not byte-identical payloads.

## OpenAPI

Where the framework generates OpenAPI (FastAPI, Litestar), the description must expose the five operations above with item schemas containing `id`, `title`, and `done`. Title/version metadata may differ. Plain-JSON examples without a generator (e.g. bare Flask) are exempt from OpenAPI expectations.
