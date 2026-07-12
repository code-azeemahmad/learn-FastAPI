# Authentication & Authorization

Our goal is not just to implement login. Our goal is to build an authentication system the way it would be built in a **production FastAPI application**.

We'll take small, logical steps.

---

## Authentication Roadmap

| Lesson | Topic                              |
|--------|-------------------------------------|
| 23     | Service Composition                 |
| 24     | Password Hashing                    |
| 25     | Signup Endpoint                     |
| 26     | Login Endpoint                      |
| 27     | JWT Deep Dive                       |
| 28     | Access Tokens                       |
| 29     | Protected Routes                    |
| 30     | Current User Dependency              |
| 31     | Refresh Tokens                      |
| 32     | Logout                              |
| 33     | Role-Based Access Control (RBAC)    |
| 34     | Permissions                         |
| 35     | OAuth2                              |

Notice we are **not** starting with JWT. A lot of tutorials do:

```
JWT → Copy code → Login works
```

You won't understand why anything exists. We'll build the foundation first.

---

## Lesson 23 — Service Composition

This is one of the biggest mindset shifts in backend engineering.

### 1. Intuition

So far, your services look like this:

```
UserService
     │
     ▼
UserRepository
```

One service. One repository. Very simple.

Now imagine a user signs up. Does creating a user only mean inserting one row into the database? No.

A real application might need to:

- Check whether the email already exists.
- Hash the password.
- Save the user.
- Create a profile.
- Send a verification email.
- Write an audit log.
- Publish a "UserRegistered" event.
- Cache the user.

One repository can't do all of that. One service shouldn't implement every technical detail either. Instead, **the service orchestrates other components.**

### Think of an Orchestra 🎼

Imagine a conductor. The conductor doesn't play violin, piano, drums, or flute. Instead, the conductor coordinates the musicians.

That's exactly what an application service does.

---

### 2. Theory

A service has two responsibilities:

1. Apply business rules.
2. Coordinate other components.

Notice something — it doesn't necessarily do the work itself.

Example:

```
AuthService
     ↓
UserRepository
     ↓
PasswordHasher
     ↓
JWTService
     ↓
EmailService
```

Each component specializes in one job. The service coordinates them.

### Compare the Two Designs

**Bad Design**

```python
class AuthService:

    def register():
        # hash password
        # SQLAlchemy query
        # send email
        # generate JWT
        # log event
        # cache user
```

Everything in one class. Soon it becomes 800 lines.

**Good Design**

```
AuthService
     ↓
PasswordHasher
     ↓
UserRepository
     ↓
EmailService
     ↓
JWTService
```

Each class has one responsibility.

---

### 3. Visual Explanation

**Current application**

```
Router
  ↓
UserService
  ↓
UserRepository
```

**Authentication module**

```
Router
  ↓
AuthService
  ├───────────────┐
  │               │
  ▼               ▼
UserRepository  PasswordHasher
  │
  ▼
Database
```

**Later**

```
Router
  ↓
AuthService
  ├───────────────┬──────────────┬─────────────┐
  ▼               ▼              ▼             ▼
UserRepository PasswordHasher JWTService EmailService
```

The service becomes the coordinator.

---

### 4. Folder Structure

We'll expand the project gradually. Our target is:

```
app/
│
├── core/
│   ├── config.py
│   ├── security.py      ← password hashing
│   └── jwt.py           ← JWT later
│
├── routers/
│   ├── users.py
│   └── auth.py
│
├── services/
│   ├── user_service.py
│   └── auth_service.py
│
├── repositories/
│   ├── user_repository.py
│   └── token_repository.py   (later)
│
├── models/
├── schemas/
├── exceptions/
├── handlers/
└── main.py
```

Notice something important: we are **not** creating everything today. We only create folders when we actually need them. That's how real projects evolve.

---

### 5. Why We Need a Separate `AuthService`

Many beginners ask: "Why not put authentication inside `UserService`?"

Good question. Let's compare.

**`UserService` Responsibilities**

- CRUD
- Find user
- Update profile
- Delete user
- List users

**`AuthService` Responsibilities**

- Register
- Login
- Verify password
- Generate JWT
- Refresh token
- Logout
- Reset password
- Email verification

These are two different domains. Authentication is not CRUD. It deserves its own service.

---

### 6. Designing Before Coding

Before writing code, let's design the registration flow.

A user sends:

```json
{
    "name": "Azeem",
    "email": "azeem@example.com",
    "password": "MyStrongPassword123!"
}
```

**Question:** What should happen, in order? Let's think like architects.

1. Validate request body (FastAPI + Pydantic)
2. Check if email already exists
3. Hash the password
4. Create the user
5. Save to the database
6. Return the created user

Later we'll add:

- Send verification email
- Write audit log
- Publish event
- Cache user

Notice that only one of those steps is a database operation.

---

### 7. What Needs to Change?

Our current `User` model probably looks like:

```python
class User(Base):
    id
    name
    email
```

That is no longer sufficient. Authentication requires a password.

So the next lesson is not writing `AuthService` yet. We first need to update our domain model.

---

### 8. Database Changes

We'll introduce a new column:

```
password_hash
```

Not `password`. **Never store plaintext passwords.**

Your model will become conceptually:

```python
class User(Base):
    id
    name
    email
    password_hash
```

Notice the name — we don't store passwords, we store password *hashes*. We'll learn exactly why in the next lesson.

---

## 9. Upcoming Lessons

### Lesson 24 — Password Hashing

You'll learn:

- Why passwords are never stored directly
- Hashing vs encryption
- Salting
- `pwdlib` (recommended for modern FastAPI) or `passlib` (legacy projects)
- Password verification

We'll also update:

- `User` model
- `UserCreate` schema
- `UserResponse` schema (making sure it never exposes the password hash)

### Lesson 25 — Signup

We'll build `POST /auth/signup` using `AuthService`, `UserRepository`, and `PasswordHasher`.

### Lesson 26 — Login

We'll verify the password and prepare for JWT generation.

---

## 10. Best Practices

As we begin authentication:

- Keep authentication separate from user management.
- Never store or return plaintext passwords.
- Keep password hashing in a dedicated component (`core/security.py`), not inside the repository.
- Let `AuthService` coordinate the registration and login workflows.

---

## Interview Questions

1. Why shouldn't authentication logic live inside `UserService`?
2. What is service composition?
3. Why should a service coordinate other components instead of doing everything itself?
4. Which component should hash passwords?
5. Which component should access the database?
6. Why is authentication considered a separate domain from user CRUD?
7. Why do we store `password_hash` instead of `password`?
8. What additional steps besides database insertion happen during user registration in a production system?

---

## Practice

Before the next lesson:

1. Think about your current `User` model.
2. Identify everywhere it will need to change to support authentication:
   - SQLAlchemy model
   - Pydantic request schema
   - Response schema
   - Repository methods
3. Make a list of which components should know about passwords and which should never see them.

---

## Mentor's Note

One small adjustment to our roadmap: we won't write `AuthService` until we have a proper password hashing component.

A service should orchestrate existing components. Right now, `PasswordHasher` doesn't exist yet, so we'd either have to write insecure placeholder code or put hashing logic directly in the service — both are poor designs.