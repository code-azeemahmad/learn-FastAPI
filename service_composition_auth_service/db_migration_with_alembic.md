# Database Migrations with Alembic

## 1. Intuition

Imagine you're building a house. Today, the blueprint is:

```
House
├── 2 Bedrooms
├── Kitchen
└── Bathroom
```

After construction, you decide: "Let's add a garage." Would you simply change the blueprint? No — the house is already built. You need a construction plan describing:

- What changes?
- In what order?
- How to apply them safely?

Databases are exactly the same.

- Your SQLAlchemy models are the blueprint.
- Your PostgreSQL database is the actual house.
- **Alembic is the construction manager.**

---

## 2. The Problem Without Alembic

Today your model is:

```python
class User(Base):
    id
    name
    email
```

Tomorrow you change it to:

```python
class User(Base):
    id
    name
    email
    password_hash
```

Will PostgreSQL automatically update? **No.**

SQLAlchemy does not synchronize your database schema. Your Python model and your database are now out of sync. You'll eventually see errors like:

```
column "password_hash" does not exist
```

or

```
NOT NULL constraint failed
```

---

## 3. What Alembic Does

Alembic keeps track of every database change.

```
Version 1

User
├── id
├── name
└── email

     ↓
  Migration
  Add password_hash
     ↓

Version 2

User
├── id
├── name
├── email
└── password_hash
```

Every teammate can now apply the exact same migration.

---

## 4. Visual Explanation

**Without Alembic:**

```
SQLAlchemy Model
      │
      ▼
   Database ❌
```

**With Alembic:**

```
SQLAlchemy Model
      │
      ▼
Generate Migration
      │
      ▼
Migration File
      │
      ▼
   Database
```

Think of migration files as **Git commits for your database schema**.

---

## 5. Why Companies Use Alembic

Imagine you're at OpenAI. There are 100 backend engineers.

- One engineer adds `last_login`.
- Another adds `profile_picture`.
- Another adds `is_verified`.

How do all developers get the same schema? **Through migration files committed to Git.** Nobody manually edits production databases.

---

## 6. Install Alembic

Inside your virtual environment:

```bash
pip install alembic
```

Then initialize it:

```bash
alembic init alembic
```

Your project will now look like:

```
project/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│
├── alembic.ini
│
├── app/
```

---

## 7. Understanding the New Files

### `alembic.ini`

Configuration for Alembic — things like database URL, migration location, logging.

### `alembic/env.py`

The bridge between Alembic and SQLAlchemy. This is where Alembic learns about your models.

### `versions/`

The most important folder. Every migration becomes one Python file.

Example:

```
versions/
001_create_users.py
002_add_password_hash.py
003_create_posts.py
004_add_last_login.py
```

Each file represents one database change.

---

## 8. Configure Alembic

In `alembic/env.py`, import your metadata.

If your `Base` lives in `app.database.base`, then:

```python
from app.database.base import Base
```

Set:

```python
target_metadata = Base.metadata
```

This tells Alembic: "Compare my models with the database."

### Database URL

Don't hardcode it — reuse your existing configuration.

For example, if your project already exposes `settings.DATABASE_URL`, set it in `env.py`:

```python
from app.core.config import settings

config.set_main_option(
    "sqlalchemy.url",
    settings.DATABASE_URL,
)
```

Now Alembic and FastAPI share the same configuration.

---

## 9. Generate Your First Migration

Before generating, update your `User` model:

```python
password_hash: Mapped[str] = mapped_column(nullable=False)
```

Then run:

```bash
alembic revision --autogenerate -m "add password_hash to users"
```

Alembic compares your SQLAlchemy models with the PostgreSQL schema and generates a migration.

---

## 10. Understanding a Migration File

You'll see something similar to:

```python
def upgrade():
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(),
            nullable=False,
        ),
    )
```

And:

```python
def downgrade():
    op.drop_column(
        "users",
        "password_hash",
    )
```

Notice two directions:

- **Upgrade** — move forward.
- **Downgrade** — roll back.

This is extremely useful if a deployment goes wrong.

---

## 11. Apply the Migration

Run:

```bash
alembic upgrade head
```

Now PostgreSQL actually gets the new column. Your model and database are synchronized.

---

## 12. Important Production Advice

**Autogenerate is a starting point, not a guarantee.** Always review the generated migration.

For example, if you rename `email` to `email_address`, Alembic might generate:

```
DROP email
ADD email_address
```

That would delete all your data. A human should instead write a rename operation.

Treat migration files like code:

- Read them.
- Review them.
- Commit them.

---

## 13. Best Practices

- Never manually edit production databases.
- Keep migration files in version control.
- One logical schema change per migration.
- Give descriptive migration messages:
  - `add_password_hash_to_users`
  - `create_posts_table`
  - `add_is_verified_to_users`
- Avoid vague names like `update`, `fix`, `changes`.

---

## 14. Common Errors

### ❌ Using `Base.metadata.create_all()`

For development demos it's okay. For production projects, Alembic becomes the source of truth. Eventually you'll stop relying on `create_all()` for schema evolution.

### ❌ Editing old migration files

Once a migration has been shared or applied, don't rewrite history. Create a new migration instead.

### ❌ Forgetting to run migrations

Changing the model alone doesn't change the database.

---

## 15. Interview Questions

1. Why does SQLAlchemy not automatically update the database schema?
2. What problem does Alembic solve?
3. What is the purpose of `upgrade()` and `downgrade()`?
4. Why should migration files be committed to Git?
5. What does `alembic revision --autogenerate` do?
6. Why should generated migrations be reviewed?
7. When should you avoid editing existing migration files?
8. What is the difference between `create_all()` and Alembic migrations?

---

## 16. Practice

1. Install Alembic.
2. Initialize it in your project.
3. Configure `env.py` to use your existing `Base.metadata`.
4. Configure it to use your existing database URL from `config.py`.
5. Add `password_hash` to the `User` model.
6. Generate a migration.
7. Review the migration file.
8. Apply it with:
   ```bash
   alembic upgrade head
   ```

---

## Mentor's Recommendation

Before we move to Lesson 26 — Signup Endpoint, actually set up Alembic and generate your first migration. Don't just read the commands — run them.

When you're done, share these three things:

1. Your `alembic/env.py`
2. The generated migration file in `alembic/versions/`
3. Any errors you encounter (if any)

We'll review them like a real code review. Once that's in place, we'll build the signup flow using `AuthService`, password hashing, and the migrated `password_hash` column. This mirrors the workflow you'd follow on a professional backend team.