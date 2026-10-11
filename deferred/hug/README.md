# hug — deferred (blocked)

Status: blocked on this toolchain (Python 3.14), verified by the compatibility gate.

## Reason

`hug==2.6.1` (latest release, 2020) hard-pins `falcon==2.0.0`, which does
`import cgi` in `falcon/vendor/mimeparse/mimeparse.py`. The `cgi` stdlib
module was removed in Python 3.13, so `import hug` fails with
`ModuleNotFoundError: No module named 'cgi'`.

## What would unblock it

- A new hug release relaxing the falcon pin, or
- Running the matrix on an older interpreter (out of scope for this repo).

Per the repo's compatibility-gate rule this is recorded, not worked around.
