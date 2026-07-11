# SQL Querying with SQLAlchemy

## Learning Objectives

By the end of this lesson, you'll know how to:

- Retrieve records
- Filter records
- Sort records
- Paginate results
- Count rows
- Search data
- Use `first()`, `one()`, `all()`
- Understand how SQLAlchemy translates to SQL

---

## 1. Intuition

Imagine this `users` table:

| id | name  | email             |
|----|-------|-------------------|
| 1  | Azeem | azeem@gmail.com   |
| 2  | Ali   | ali@gmail.com     |
| 3  | Sara  | sara@gmail.com    |
| 4  | Ahmed | ahmed@gmail.com   |

Suppose the client asks:

```
GET /users
```

Should we return:
- One user?
- All users?
- Only Sara?
- Only users whose name starts with "A"?

The answer depends on the query we write.

---

## 2. Visual Overview

```
Browser
   │
   GET /users?name=Ali
   │
   ▼
FastAPI
   │
   SQLAlchemy Query
   │
   ▼
PostgreSQL
   │
   Returns Matching Rows
   │
   ▼
JSON Response
```

---

## 3. Getting All Records

```python
users = db.query(User).all()
```

SQL generated:

```sql
SELECT * FROM users;
```

`.all()` returns:

```python
[
    User(...),
    User(...),
    User(...),
]
```

Use when you want every matching row.

---

## 4. Getting the First Record

```python
user = db.query(User).first()
```

SQL:

```sql
SELECT * FROM users LIMIT 1;
```

Returns a `User(...)` object, or `None` if no rows exist.

### When is `first()` useful?

```python
user = (
    db.query(User)
    .filter(User.email == email)
    .first()
)
```

If the email isn't found, this returns `None` — no exception is raised.

---

## 5. Filtering

Suppose:

```
GET /users/2
```

Query:

```python
user = (
    db.query(User)
    .filter(User.id == 2)
    .first()
)
```

Generated SQL:

```sql
SELECT * FROM users WHERE id = 2 LIMIT 1;
```

### Multiple Filters

```python
user = (
    db.query(User)
    .filter(
        User.name == "Ali",
        User.email == "ali@gmail.com",
    )
    .first()
)
```

SQL:

```sql
SELECT * FROM users
WHERE name = 'Ali' AND email = 'ali@gmail.com';
```

---

## 6. Sorting

```
GET /users
```

You want alphabetical order.

```python
from sqlalchemy import asc

users = (
    db.query(User)
    .order_by(asc(User.name))
    .all()
)
```

SQL: `ORDER BY name ASC;`

Descending:

```python
from sqlalchemy import desc

users = (
    db.query(User)
    .order_by(desc(User.id))
    .all()
)
```

Newest users first.

### Visual

Before sorting: `Sara, Ali, Azeem`

Ascending: `Ali, Azeem, Sara`

Descending: `Sara, Azeem, Ali`

---

## 7. Counting Rows

Sometimes you don't need data — only the number of rows.

```python
total_users = db.query(User).count()
```

SQL:

```sql
SELECT COUNT(*) FROM users;
```

Useful for:
- Dashboard statistics
- Analytics
- Pagination metadata

---

## 8. Pagination

Imagine 10 million users. Should we return all of them? No.

Instead:

```
GET /users?page=1
```

or

```
GET /users?skip=0&limit=10
```

FastAPI:

```python
@router.get("/")
def get_users(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
```

Query:

```python
users = (
    db.query(User)
    .offset(skip)
    .limit(limit)
    .all()
)
```

SQL:

```sql
SELECT * FROM users LIMIT 10 OFFSET 0;
```

### Visual

Users: `1 2 3 4 5 6 7 8 9 10 11 12`

Request: `skip=5, limit=3` → Returns: `6 7 8`

### Why Pagination Matters

Companies like Amazon, Netflix, and LinkedIn never send thousands of records at once.

Reasons:
- Faster responses
- Lower memory usage
- Better user experience
- Reduced network traffic

---

## 9. Searching

```
GET /users?search=Ali
```

We'll use SQL's `LIKE`.

```python
users = (
    db.query(User)
    .filter(
        User.name.like("%Ali%")
    )
    .all()
)
```

Generated SQL:

```sql
WHERE name LIKE '%Ali%';
```

Matches: `Ali`, `Ali Khan`, `Muhammad Ali`

---

## 10. Combining Everything

```
GET /users?search=a
```

Query:

```python
users = (
    db.query(User)
    .filter(
        User.name.like("%a%")
    )
    .order_by(User.name)
    .offset(0)
    .limit(5)
    .all()
)
```

Flow:

```
Users → Filter → Sort → Pagination → Return Results
```

This pattern is extremely common in production APIs.

---

## 11. one() vs first() vs all()

This is a favorite interview topic.

### `all()`

```python
db.query(User).all()
```

Returns: `list[User]`

### `first()`

```python
db.query(User).first()
```

Returns: `User` or `None`

### `one()`

```python
db.query(User).one()
```

Returns exactly one row. If there are zero rows or multiple rows, it raises an exception.

Use it only when you're certain exactly one row should exist.

### Comparison

| Method    | Returns          | Raises Exception              |
|-----------|-------------------|-------------------------------|
| `all()`   | List              | No                             |
| `first()` | Object or None    | No                             |
| `one()`   | One object        | Yes, if not exactly one row    |

---

## 12. Best Practices

- Always paginate large datasets.
- Filter in the database, not in Python.
- Use indexes on frequently searched columns (covered later).
- Prefer `first()` when "not found" is acceptable.
- Use ordering for predictable results.

---

## 13. Common Beginner Mistakes

### Mistake 1 — Filtering in Python instead of SQL

Wrong:

```python
users = db.query(User).all()
for user in users:
    ...  # filtering here
```

Right — filter in SQLAlchemy:

```python
.filter(...)
```

The database is optimized for searching.

### Mistake 2 — Returning every row

Bad for a million-row table:

```python
.all()
```

Always paginate.

### Mistake 3 — Forgetting to execute the query

This returns a query object, not the data:

```python
db.query(User)
```

You need `.first()` or `.all()` to execute it.

---

## 14. Real-World Example

Imagine an e-commerce API:

```
GET /products?search=laptop&sort=price&limit=20&offset=40
```

The query:

```python
products = (
    db.query(Product)
    .filter(Product.name.like("%laptop%"))
    .order_by(Product.price)
    .offset(40)
    .limit(20)
    .all()
)
```

This exact pattern powers product catalogs across the web.

---

## 15. Interview Questions

1. What is the difference between `all()` and `first()`?
2. When would you use `one()`?
3. Why is pagination important?
4. What does `offset()` do?
5. What does `limit()` do?
6. Why should filtering happen in SQL rather than Python?
7. What SQL does `.count()` generate?
8. Why is ordering useful?

---

## 16. Practice

### Exercise 1

Extend your `GET /users` endpoint to support `skip` and `limit`.

Test:
```
/users?skip=0&limit=5
/users?skip=5&limit=5
```

### Exercise 2

Add a `search` parameter:

```
/users?search=Ali
```

Return users whose names contain the search text.

### Exercise 3

Add sorting:

```
/users?sort=asc
/users?sort=desc
```

Sort by `id`.

---

## 17. Revision

### Key Concepts

- `.all()` returns all matching rows.
- `.first()` returns the first matching row or `None`.
- `.one()` expects exactly one matching row.
- `.filter()` adds WHERE conditions.
- `.order_by()` sorts results.
- `.limit()` restricts the number of rows.
- `.offset()` skips rows for pagination.
- `.count()` returns the number of matching rows.

### A Senior Backend Engineer's Perspective

The examples in this lesson use the classic SQLAlchemy Query API:

```python
db.query(User).filter(...).all()
```

You will still encounter this style in many production codebases, tutorials, and interview questions.

However, SQLAlchemy 2.0 encourages a newer approach using `select()`:

```python
from sqlalchemy import select

statement = select(User).where(User.id == 1)
result = db.execute(statement)
user = result.scalar_one_or_none()
```

Both approaches are important:

- Know the **Query API** because you'll see it in existing projects and interviews.
- Learn the **`select()` API** because it's the modern SQLAlchemy 2.x style and where the ecosystem is heading.