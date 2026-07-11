# One-to-Many Relationships in SQLAlchemy

## Learning Objectives

By the end of this lesson, you'll understand:

- How One-to-Many relationships work
- How to create related records
- How SQLAlchemy connects objects automatically
- What `back_populates` actually does
- How to navigate relationships
- How SQLAlchemy generates SQL behind the scenes

---

## 1. Intuition

Imagine a blog website. One user writes many posts.

```
Azeem
│
├── Learning FastAPI
├── SQLAlchemy Guide
├── Docker Tutorial
└── Python Tips
```

This is a **One-to-Many** relationship. One User → Many Posts.

---

## 2. Database Design

Let's look at the tables.

**Users**

| id | name  |
|----|-------|
| 1  | Azeem |

**Posts**

| id | title      | user_id |
|----|------------|---------|
| 1  | FastAPI    | 1       |
| 2  | SQLAlchemy | 1       |
| 3  | Docker     | 1       |

Notice something important: the `users` table does **not** contain a list of posts. Instead, every post stores the ID of its owner.

```
Users
   ▲
   │
user_id
   │
Posts
```

This is how relational databases work.

---

## 3. SQLAlchemy Models

Let's review the models.

### User Model

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

### Post Model

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

---

## 4. Understanding `back_populates`

This is one of the most misunderstood concepts.

```
User Object
   posts
     │
     ▼
Post Object
   author
```

The two properties point to each other. That means `user.posts` works, **and** `post.author` also works.

Without `back_populates`, SQLAlchemy wouldn't know these two relationships represent the same connection.

---

## 5. Creating Related Objects

```python
user = User(
    name="Azeem",
    email="azeem@gmail.com",
)
```

Now create posts:

```python
post1 = Post(
    title="Learning FastAPI",
    content="..."
)

post2 = Post(
    title="SQLAlchemy",
    content="..."
)
```

Instead of manually assigning IDs:

```python
post1.user_id = user.id
```

you can simply write:

```python
post1.author = user
post2.author = user
```

SQLAlchemy automatically sets the foreign key when the objects are persisted.

### Visual

```
User Object
     ↓
Post.author = user
     ↓
SQLAlchemy
     ↓
user_id assigned automatically
     ↓
Database
```

---

## 6. The Reverse Direction

You can also work from the parent side.

```python
user.posts.append(post1)
user.posts.append(post2)
```

Again, no need to manually set `user_id`. SQLAlchemy keeps both sides synchronized.

### Visual

```
user.posts
     ↓
Append Post
     ↓
SQLAlchemy
     ↓
Updates post.author
     ↓
Updates user_id
```

---

## 7. Saving Everything

```python
db.add(user)
db.commit()
```

That's it.

Even though you only added the `User`, SQLAlchemy can also persist the related `Post` objects because they're connected through the relationship and, by default, the relationship includes a save-update cascade.

**Result:**

users: `1, Azeem`

posts: `1, Learning FastAPI, 1` and `2, SQLAlchemy, 1`

---

## 8. Reading Relationships

Suppose you fetch:

```python
user = (
    db.query(User)
    .filter(User.id == 1)
    .first()
)
```

Now:

```python
print(user.posts)
```

returns:

```python
[
    Post(...),
    Post(...),
]
```

You never queried `SELECT * FROM posts` directly in your Python code — SQLAlchemy handled it.

### The Reverse

```python
post = (
    db.query(Post)
    .first()
)

print(post.author)
```

returns:

```python
User(...)
```

Again, no manual query.

---

## 9. Under the Hood

When you access:

```python
user.posts
```

SQLAlchemy executes SQL similar to:

```sql
SELECT * FROM posts WHERE user_id = 1;
```

When you access:

```python
post.author
```

It executes SQL similar to:

```sql
SELECT * FROM users WHERE id = post.user_id;
```

The ORM translates object access into SQL queries.

---

## 10. Understanding `cascade`

Remember this?

```python
cascade="all, delete-orphan"
```

What does it mean?

Imagine:

```python
db.delete(user)
```

Should the posts remain? Probably not.

With `cascade="all, delete-orphan"`, deleting the user also deletes their related posts.

```
Delete User
     ↓
Delete Posts
     ↓
Database Consistent
```

Without a cascade strategy, deleting a parent may fail because child rows still reference it, or it may leave orphaned data depending on your database constraints and configuration.

---

## 11. Real-World Example

Think of GitHub.

```
User → Repositories
```

One user. Many repositories. You can do `user.repositories` — exactly the same pattern.

---

## 12. Best Practices

- Prefer working with relationships instead of manually managing foreign keys when you already have the related objects.
- Use clear relationship names: `author`, `posts`, `comments`, `orders`.
- Keep `back_populates` consistent on both sides.
- Think carefully before using cascading deletes in production — ensure they match your business rules.

---

## 13. Common Beginner Mistakes

### Mistake 1

Doing:

```python
post.user_id = 1
```

even when:

```python
post.author = user
```

is available. Using the relationship keeps your code more expressive and lets SQLAlchemy synchronize the foreign key.

### Mistake 2

Forgetting `relationship(...)`. The foreign key alone creates the database relationship, but without the ORM relationship you lose convenient object navigation like `user.posts`.

### Mistake 3

Using different names.

Bad:

```python
posts
owner
```

when `back_populates="author"` expects `author`. Both sides must reference each other's relationship names correctly.

---

## 14. Interview Questions

1. What is a One-to-Many relationship?
2. Where is the foreign key stored?
3. What does `relationship()` do?
4. What is `back_populates`?
5. Can `relationship()` create database columns?
6. What does `cascade="all, delete-orphan"` do?
7. Why is `post.author = user` often preferred over assigning `user_id` directly?
8. What SQL is generated when accessing `user.posts`?

---

## 15. Practice

### Exercise 1

Create one user and three posts. Associate them using `post.author = user`. Save them to PostgreSQL.

### Exercise 2

Retrieve a user. Print `user.posts`. Verify all related posts are returned.

### Exercise 3

Retrieve a post. Print `post.author`. Verify it returns the associated user.

---

## 16. Revision

### Key Concepts

- One-to-Many means one parent has many children.
- The foreign key lives on the "many" side (`posts.user_id`).
- `relationship()` provides object-level navigation.
- `back_populates` connects the relationship from both directions.
- SQLAlchemy automatically keeps related objects synchronized.

---

## A Senior Backend Engineer's Perspective

Today you saw the convenience of writing `user.posts` instead of manually querying the posts table.

However, there's an important question: **When does SQLAlchemy actually fetch those posts?**

Does it:

- Fetch them immediately with the user?
- Wait until you access `user.posts`?
- Fetch them in a single query?
- Fetch them with additional queries?

These choices affect application performance.

For example, if you load 100 users and then access `user.posts` for each one, you might accidentally execute 101 SQL queries — a classic performance issue known as the **N+1 query problem**.

The solution involves understanding **Lazy Loading** and **Eager Loading**, which we'll cover next. Mastering those concepts is essential for writing efficient, scalable APIs and is a topic that frequently comes up in backend interviews.