# Todo behavior

Shared domain behavior for all examples. Both contracts (`json-api.md`, `server-rendered.md`) expose this behavior through their own interface.

## Item

- `id`: unique identifier, assigned by the server. Opaque to clients (integer or string, per framework idiom).
- `title`: non-empty string, required at creation.
- `done`: boolean, defaults to `false`.

## Operations

1. **List** all items.
2. **Create** an item with a title.
3. **Toggle** an item between done and not done (or set explicitly, per contract).
4. **Delete** an item.

## Validation

- Empty or missing title is rejected (see per-contract error behavior).
- Unknown ids are reported as not found (see per-contract error behavior).

## Storage minimum

Both backends preserve the above behavior:

- **In-memory:** process-local store, seeded empty. Data loss on restart is acceptable.
- **SQLite:** persisted store via the framework-idiomatic integration. Schema and setup differ per example, but the observable behavior above must match in-memory.
