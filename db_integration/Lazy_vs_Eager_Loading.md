# Lazy Loading, Eager Loading & the N+1 Query Problem

## Learning Objectives

By the end of this lesson, you'll understand:

- What Lazy Loading is
- What Eager Loading is
- The N+1 Query Problem
- `joinedload()`
- `selectinload()`
- When to use each loading strategy
- How SQLAlchemy decides when to fetch related data

---

## 1. Intuition

Imagine you order food from a restaurant.

### Lazy Loading

You order:

```
🍔 Burger
```

The waiter brings the burger. Later you ask, "Can I also have fries?" — the waiter goes back to the kitchen. Later: "Can I have a Coke?" — another trip.

**Each request causes another trip.**

### Eager Loading

Instead:

```
Burger
Fries
Coke
```

Everything comes together. **Only one trip.**

Databases behave exactly the same way.

---

## 2. What is Lazy Loading?

```python
user = (
    db.query(User)
    .filter(User.id == 1)
    .first()
)
```

SQL executed:

```sql
SELECT * FROM users WHERE id = 1;
```

Only the `User` is loaded.

Now you do:

```python
print(user.posts)
```

SQLAlchemy notices posts haven't been loaded yet, so it executes another query:

```sql
SELECT * FROM posts WHERE user_id = 1;
```

This behavior is called **Lazy Loading**.

### Visual

```
Query User
    ↓
User Loaded
    ↓
Access user.posts
    ↓
Another SQL Query
    ↓
Posts Loaded
```

The related data is fetched only when it's first accessed.

---

## 3. Why Lazy Loading Exists

Imagine every user has 500 posts, 10,000 comments, and 2,000 likes. If SQLAlchemy always loaded everything, `get_user()` would be extremely expensive.

Instead: **load only what you ask for.** This saves memory and bandwidth when you don't need the related data.

---

## 4. The N+1 Query Problem

This is one of the most common performance issues.

```python
users = db.query(User).all()
```

Suppose there are 100 users.

SQL: `SELECT * FROM users;` — **one query.**

Now:

```python
for user in users:
    print(user.posts)
```

For each user:

```sql
SELECT * FROM posts WHERE user_id = ?
```

If there are 100 users: **1 query + 100 queries = 101 SQL queries.**

This is called the **N+1 Query Problem**.

### Visual

```
Load Users
    ↓
1 Query
    ↓
Loop
    ↓
User 1 → Query
User 2 → Query
User 3 → Query
...
User 100 → Query

Total: 101 queries. Very slow.
```

---

## 5. How to Solve It

SQLAlchemy provides **Eager Loading** — the idea is to load related data up front.

---

## 6. `joinedload()`

```python
from sqlalchemy.orm import joinedload

users = (
    db.query(User)
    .options(joinedload(User.posts))
    .all()
)
```

Now SQLAlchemy generates SQL similar to:

```sql
SELECT
users.*,
posts.*
FROM users
LEFT OUTER JOIN posts
ON users.id = posts.user_id;
```

Everything comes in **one query**.

### Visual

```
Users
  JOIN
Posts
    ↓
One Query
    ↓
Everything Loaded
```

---

## 7. Understanding JOIN

**Users**

| id | name  |
|----|-------|
| 1  | Azeem |

**Posts**

| id | title   | user_id |
|----|---------|---------|
| 1  | FastAPI | 1       |
| 2  | Docker  | 1       |

**Result of the join:**

| User  | Post    |
|-------|---------|
| Azeem | FastAPI |
| Azeem | Docker  |

Notice: the user data appears multiple times because each post produces a row. SQLAlchemy reconstructs this into `user.posts` automatically.

---

## 8. `selectinload()`

Another loading strategy.

```python
from sqlalchemy.orm import selectinload

users = (
    db.query(User)
    .options(selectinload(User.posts))
    .all()
)
```

Instead of 101 queries, SQLAlchemy does:

**Query 1:**

```sql
SELECT * FROM users;
```

**Query 2:**

```sql
SELECT * FROM posts WHERE user_id IN (1,2,3,...100);
```

Only **two queries**.

### Visual

```
Users
   ↓
Query 1
   ↓
Collect User IDs
   ↓
Query 2
   ↓
Load All Posts
```

---

## 9. `joinedload()` vs `selectinload()`

| Feature                                | `joinedload()`                                       | `selectinload()`                     |
|-----------------------------------------|-------------------------------------------------------|----------------------------------------|
| SQL Queries                              | 1                                                       | 2                                       |
| Uses JOIN                                | Yes                                                      | No                                       |
| Duplicates parent rows in SQL result     | Yes                                                     | No                                       |
| Better For                               | One-to-One, Many-to-One, or small child collections     | One-to-Many with many child rows        |

### Which One Should You Use?

- One user, three posts → `joinedload()` is great.
- One user, 100,000 comments → a single JOIN result becomes huge because each user row is repeated for every comment. In many One-to-Many cases, `selectinload()` is more efficient.

There isn't a universal winner — choose based on your data and measure performance.

---

## 10. Real-World Example

Imagine an e-commerce site's home page:

```
Products → Categories → Images
```

If every product causes another query:

```
100 Products
   ↓
100 Category Queries
   ↓
100 Image Queries
```

Terrible performance. Instead: **use eager loading.**

---

## 11. SQLAlchemy 2.0 Style

You've learned:

```python
db.query(User)
```

Modern SQLAlchemy prefers:

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

statement = (
    select(User)
    .options(selectinload(User.posts))
)

result = db.execute(statement)

users = result.scalars().all()
```

This is the style we'll increasingly adopt moving forward.

---

## 12. Best Practices

- Understand how many queries your code executes.
- Don't use eager loading for every relationship by default.
- Avoid the N+1 problem in loops.
- Choose `selectinload()` or `joinedload()` based on the relationship and data size.
- Use SQL logging (`echo=True`) during development to see the generated SQL.

---

## 13. Common Beginner Mistakes

### Mistake 1

```python
for user in users:
    print(user.posts)
```

without considering the extra queries. Always think about what's happening behind the scenes.

### Mistake 2

Using `joinedload()` for every relationship. Large joins can become inefficient.

### Mistake 3

Loading relationships you never use. Only fetch the data you actually need.

---

## 14. Interview Questions

1. What is Lazy Loading?
2. What is Eager Loading?
3. Explain the N+1 Query Problem.
4. What does `joinedload()` do?
5. What does `selectinload()` do?
6. When would you prefer `selectinload()` over `joinedload()`?
7. Why can large JOINs become inefficient?
8. How can you inspect the SQL generated by SQLAlchemy?

---

## 15. Practice

### Exercise 1

Enable `echo=True` in your SQLAlchemy engine. Run:

```python
user = db.query(User).first()
print(user.posts)
```

Observe the SQL statements printed to the terminal. How many queries were executed?

### Exercise 2

Modify the query to use `joinedload(User.posts)`. Compare the SQL output.

### Exercise 3

Repeat using `selectinload(User.posts)`. Compare:

- Number of queries
- SQL statements
- Which approach you think is more suitable for your sample data

---

## 16. Revision

### Key Concepts

- Lazy Loading fetches related data only when accessed.
- Eager Loading fetches related data in advance.
- The N+1 Query Problem occurs when one initial query triggers many additional queries.
- `joinedload()` typically uses a SQL JOIN.
- `selectinload()` typically uses two queries with an IN clause.
- The best loading strategy depends on the relationship and the amount of related data.

---

## A Senior Backend Engineer's Perspective

So far, we've focused on reading related data efficiently. The next important question is: **what happens when multiple database operations must either all succeed or all fail?**

Imagine a banking application:

1. Deduct $100 from Account A.
2. Add $100 to Account B.

If the server crashes after step 1 but before step 2, the money has effectively disappeared.

Databases solve this with **transactions**. Transactions guarantee that a group of operations is treated as a single unit of work:

- Either everything succeeds and is committed.
- Or everything is rolled back and the database remains consistent.

This is one of the most critical concepts in backend development, and it's our next lesson before we move on to the modern SQLAlchemy 2.x querying style and Alembic migrations.