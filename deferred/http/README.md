# http (stdlib) — deferred (no framework idiom)

Status: deferred by design, not evaluated further.

## Reason

The stdlib `http` module (`http.server` handlers) has no routing or
rendering idiom to compare — a handler-based todo app would only
demonstrate hand-rolled dispatch, which teaches nothing about
framework shape.

## What would unblock it

Nothing planned. The stdlib `socket` module is deferred for the same reason.
