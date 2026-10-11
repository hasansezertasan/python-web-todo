# eve — deferred (blocked)

Status: blocked, verified by the compatibility gate on Python 3.14.

## Reason

Three compounding problems, any one of which blocks a self-contained example:

1. Eve's default data layer is MongoDB — an external service, out of
   scope for examples that must boot with no infrastructure.
2. Even with MongoDB, Eve 2.3.1's mongo layer is broken against modern
   PyMongo: reads fail with
   `TypeError: 'Collection' object is not callable`
   (Eve calls the `collection.count()` API removed in PyMongo 4),
   so `GET` answers 500.
3. The SQL escape hatch (`eve-sqlalchemy`) does not resolve on a modern
   toolchain — it drags in `eve<0.8` / `cerberus 0.9.2`, whose build fails.

## What would unblock it

- An Eve release supporting current PyMongo without a mandatory
  external database, or
- A maintained SQL backend working on current Python/SQLAlchemy.
