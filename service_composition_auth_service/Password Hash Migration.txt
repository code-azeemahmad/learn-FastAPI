# Adding `password_hash` to the Users Table

## Current State

Your database currently has:

```
users
├── id
├── name
└── email
```

Your SQLAlchemy model now has:

```
users
├── id
├── name
├── email
└── password_hash   ← NEW
```

So Alembic should detect exactly **one** schema difference: add the `password_hash` column to the `users` table.

---

## Before Generating the Migration

There's one important thing to think about.

Your model currently says:

```python
password_hash: Mapped[str] = mapped_column(nullable=False)
```

This means:

```sql
password_hash VARCHAR NOT NULL
```

But your existing users don't have a password hash.

Imagine PostgreSQL trying to do this:

**Current rows**

| id | name  | email            |
|----|-------|------------------|
| 1  | Azeem | azeem@gmail.com  |
| 2  | Ali   | ali@gmail.com    |

Now Alembic says:

```sql
ALTER TABLE users
ADD COLUMN password_hash VARCHAR NOT NULL;
```

PostgreSQL replies: *"What value should I put in `password_hash` for the existing rows? It can't invent one."*

The migration will likely fail unless you provide a default or use a staged migration.

---

## The Production Way

In real projects, you'd typically do this in **two migrations**:

**Migration 1**
```
password_hash
nullable=True
```
Populate hashes for existing users (or require password resets).

**Migration 2**
```
password_hash
nullable=False
```

This avoids breaking existing data.

---

## For Your Learning Project

Since these are only test users, you have two reasonable options.

### Option 1 (Recommended)

Delete the existing test users. Then generate the migration.

When the table has no rows, adding a non-nullable column is straightforward.

### Option 2

Keep the users. Let Alembic generate the migration, then manually edit it to provide a temporary server default or perform a staged migration.

This is a valuable production technique, but it's a bit more advanced for a first migration.

---

## One More Thing Before Generating

Earlier, this was spotted in `database.py`:

```python
from app.core.config import DATABASE_URL
```

Since the configuration has changed to use:

```python
settings = Settings()
```

please update `database.py` to:

```python
from app.core.config import settings
```

and:

```python
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,
)
```

This ensures FastAPI and Alembic are using the same configuration source.

---

## Then You're Ready

Once `database.py` is fixed, run:

```bash
alembic revision --autogenerate -m "add password_hash to users"
```

Paste the generated migration file for review **before** running:

```bash
alembic upgrade head
```

---

## Review Checklist (for the generated migration)

- [ ] Only `password_hash` is touched — no accidental drops/renames on other columns
- [ ] `nullable` and any `server_default` are set as intended
- [ ] `downgrade()` correctly reverses the change