# socket (stdlib) — deferred (no framework idiom)

Status: deferred by design, not evaluated further.

## Reason

The stdlib `socket` module is a networking primitive, not a web
framework. There is no routing, request-handling, or rendering idiom to
compare — a socket-based todo app would only demonstrate hand-rolled
HTTP parsing, which teaches nothing about framework shape.

## What would unblock it

Nothing planned. The stdlib `http` module is deferred for the same reason.
