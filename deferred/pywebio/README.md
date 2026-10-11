# pywebio — deferred (needs a UI track)

Status: deferred by design, not evaluated for install compatibility.

## Reason

PyWebIO writes web interaction as plain sync-style IO functions, not as
routed HTTP services. It exposes neither the JSON API surface
(`specs/json-api.md`) nor the server-rendered page/form flows
(`specs/server-rendered.md`), so there is nothing fair to compare
against the `api`/`ssr` examples.

## What would unblock it

A separate UI-track spec defining comparable app behavior
(a shared layout, a shared interaction, and how to verify it).
