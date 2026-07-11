# Advanced Database Design — Relationships & Foreign Keys

This section is where you transition from "I can build CRUD APIs" to "I understand how real backend databases are designed."

We'll build everything around a single project that grows with each lesson.

---

## Our Project

Instead of random examples, we'll use a **Blog API**, because it naturally demonstrates relationships.

The entities will evolve like this:

```
User
│
├── id
├── name
└── email

↓

Post
│
├── id
├── title
├── content
└── user_id

↓

Comment
│
├── id
├── text
├── post_id
└── user_id

↓

Tag
│
├── id
└── name

↓

PostTag
│
├── post_id
└── tag_id
```

With this single project, you'll learn:

- One-to-Many (User → Posts)
- One-to-Many (Post → Comments)
- Many-to-Many (Posts ↔ Tags)
- Foreign Keys
- Joins
- Lazy Loading
- Eager Loading
- Transactions

By the end, you'll understand how most production databases are structured.

---

## Lesson 15 — Relationships & Foreign Keys

This is one of the most important lessons in database design.

If you truly understand today's lesson, then:

- Building an E-commerce backend becomes much easier.
- Building authentication becomes much easier.
- Building AI applications with users, conversations, and documents becomes much easier.

### Learning Objectives

By the end of this lesson, you'll understand:

- What relationships are
- Why foreign keys exist
- How SQLAlchemy models relationships
- Why databases don't duplicate data
- How to model real-world systems

---

## 1. Intuition

Imagine Instagram.

A user can create many posts.

Should Instagram store the user's name inside every post?

### Bad Design

| Post ID | Title             | User Name |
|---------|--------------------|-----------|
| 1       | My Vacation        | Azeem     |
| 2       | Learning FastAPI    | Azeem     |
| 3       | Python Tips         | Azeem     |

What happens if the user changes their name? Now you must update every row. If they have 10, 1,000, or 100,000 posts — that's a lot of duplicated data.

### Good Design

**Users**

| id | name  |
|----|-------|
| 1  | Azeem |

**Posts**

| id | title   | user_id |
|----|---------|---------|
| 1  | Vacation| 1       |
| 2  | FastAPI | 1       |
| 3  | Python  | 1       |

Now, if the user changes their name:

```
Users Table

Azeem
  ↓
Muhammad Azeem
```

Every post still points to the same user through `user_id`. Only one row changes.

This avoids data duplication and keeps the database consistent.

---

## 2. What Is a Relationship?

A relationship is a connection between two tables.

```
Users
  id
  name
   ↓
 user_id
   ↓
Posts
  id
  title
```

The arrow is the relationship.

---

## 3. What Is a Foreign Key?

A **primary key** uniquely identifies a row.

```
Users
id = 1
```

A **foreign key** stores the primary key from another table.

```
Posts
user_id = 1
```

`user_id` points to `Users.id`.

Think of a foreign key as a **reference, not a copy**.

### Visual

```
Users
+----+--------+
| id | name   |
+----+--------+
| 1  | Azeem  |
| 2  | Ali    |
+----+--------+
           ▲
           │
Posts      │
+----+-------------+---------+
| id | title       | user_id |
+----+-------------+---------+
| 1  | FastAPI     |    1    |
| 2  | SQLAlchemy  |    1    |
| 3  | Docker      |    2    |
+----+-------------+---------+
```

---

## 4. Why Are Foreign Keys Important?

Suppose someone tries to create `user_id = 999`, but user 999 doesn't exist.

**Without a foreign key:** the database allows invalid data.

**With a foreign key:**

```
ERROR
Foreign Key Constraint Failed
```

The database protects your data.

---

## 5. Real-World Examples

### E-commerce

```
Customer → Orders → Order Items → Products
```

Each order belongs to one customer.

### Banking

```
Customer → Bank Account → Transactions
```

Each transaction belongs to one account.

### ChatGPT

```
User → Conversation → Messages
```

A message belongs to one conversation.

### RAG System

```
User → Document → Chunks → Embeddings
```

Every embedding belongs to a chunk. Every chunk belongs to a document. Every document belongs to a user.

This is why relationships are so important for AI systems.

---

## 6. Relationship Types

There are three major relationship types you'll use most often.

### One-to-One (1:1)

```
User → Profile
```

One user has one profile. One profile belongs to one user.

We'll learn this after One-to-Many.

### One-to-Many (1:N)

The most common relationship.

```
User → Posts, Posts, Posts
```

One user. Many posts.

Examples:
- User → Orders
- Category → Products
- Company → Employees
- Teacher → Students (depending on the model)

### Many-to-Many (N:M)

```
Students ↕ Courses
```

One student takes many courses. One course has many students.

This requires a **junction (association) table**. We'll build this with `Post` and `Tag`.

---

## 7. SQLAlchemy Model (First Step)

Let's update our models.

### User

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
```

Notice `posts`: there is no `posts` column in the database. `relationship()` is an ORM feature that tells SQLAlchemy how tables are connected.

### Post

```python
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str] = mapped_column(String(200))

    content: Mapped[str]

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    author: Mapped["User"] = relationship(
        back_populates="posts"
    )
```

### Code Walkthrough

**Foreign Key**

```python
user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id")
)
```

This creates a database column `user_id` and adds a constraint that it must reference `users.id`.

**Relationship**

```python
author = relationship(...)
```

This does **not** create a database column. It creates a Python attribute so you can write `post.author` instead of manually querying the users table.

**`back_populates`**

These two lines:

```python
posts = relationship(back_populates="author")
```

and

```python
author = relationship(back_populates="posts")
```

tell SQLAlchemy that these relationships describe the same connection from opposite directions. That gives you convenient navigation: `user.posts` and `post.author`.

### Visual

```
Python Objects

User
│
├── id
├── name
└── posts  ───────────────┐
                           │
                           ▼
                    Post
                    │
                    ├── id
                    ├── title
                    ├── user_id
                    └── author
```

---

## 8. Database View

After creating the tables:

**users**

```
id
name
email
```

**posts**

```
id
title
content
user_id
```

Notice: there is **no** `author` column. `author` exists only in Python. The database stores only the foreign key (`user_id`).

This distinction is very important.

---

## 9. Best Practices

- Use foreign keys to enforce referential integrity.
- Store IDs, not duplicated data.
- Name foreign keys clearly (`user_id`, `post_id`, `order_id`).
- Use `relationship()` to make navigation easier in Python.

---

## 10. Common Beginner Mistakes

### Mistake 1

Storing `author_name` inside the `posts` table instead of a `user_id`. This duplicates data.

### Mistake 2

Thinking `relationship()` creates a database column. It doesn't — only `mapped_column()` creates database columns.

### Mistake 3

Confusing `user_id` with `author`:
- `user_id` → stored in PostgreSQL.
- `author` → Python object provided by SQLAlchemy.

---

## 11. Interview Questions

1. What is a foreign key?
2. Why do databases use relationships?
3. What problem does a foreign key solve?
4. What's the difference between a primary key and a foreign key?
5. Does `relationship()` create a database column?
6. What does `back_populates` do?
7. Why is storing IDs better than storing duplicated names?

---

## 12. Practice

### Exercise 1

Draw the database design for: `User`, `Blog Post`, `Comment`. Show the primary keys and foreign keys.

### Exercise 2

Design the relationships for: `Student`, `Course`. What kind of relationship is it?

### Exercise 3

Design a simple RAG database with these entities: `User`, `Document`, `Chunk`, `Embedding`. Identify the relationships between them.

---

## 13. Revision

### Key Concepts

- A primary key uniquely identifies a row.
- A foreign key references a primary key in another table.
- `relationship()` creates Python object relationships, not database columns.
- `back_populates` links both sides of a relationship.
- Avoid duplicating data; store references instead.

---

## What's Next?

In the next lesson, we'll make these relationships come alive by learning **One-to-Many relationships in practice**.

You'll create a user, add multiple posts, and then retrieve data in both directions:

```python
user.posts
post.author
```

You'll also learn how SQLAlchemy automatically fetches related objects, which sets the stage for understanding lazy loading, eager loading, and joins. These are core skills for building efficient, production-ready APIs.