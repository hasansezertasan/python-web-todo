# Deferred frameworks

One folder per deferred framework, each with a README explaining why it
has no example. Two kinds of deferral:

- **Blocked** (`hug`): fails the compatibility gate on this toolchain.
- **Out of scope** (UI/data-app frameworks, stdlib primitives): no fair
  comparison exists under the current `api`/`ssr` contracts.

| Folder | Kind | One-line reason |
| ------ | ---- | --------------- |
| `hug/` | Blocked | `falcon==2.0.0` pin imports removed `cgi` module |
| `eve/` | Blocked | Needs MongoDB; mongo layer broken with PyMongo 4; SQL alt stale |
| `dash/` | UI track needed | Dashboard callbacks, not routes |
| `streamlit/` | UI track needed | Script-rerun apps, not routed services |
| `nicegui/` | UI track needed | Component events, not HTTP contracts |
| `reflex/` | UI track needed | Compiled reactive apps |
| `gradio/` | UI track needed | ML demo UIs |
| `flet/` | UI track needed | Desktop/mobile UI, not HTTP services |
| `pywebio/` | UI track needed | Sync-style IO functions |
| `socket/` | No framework idiom | Hand-rolled HTTP teaches no framework shape |
| `http/` | No framework idiom | Hand-rolled dispatch teaches no framework shape |
