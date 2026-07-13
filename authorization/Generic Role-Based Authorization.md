# Generic Role-Based Authorization

## Why `require_admin()` Isn't Enough

Imagine six months from now your application grows. You add these roles:

```
admin
moderator
support
editor
user
```

Now consider these endpoints:

| Endpoint          | Allowed Roles              |
|--------------------|------------------------------|
| Delete User          | `admin`                       |
| Ban User               | `admin`, `moderator`             |
| Refund Order             | `admin`, `support`                  |
| Publish Article             | `admin`, `editor`                      |
| Dashboard                       | all authenticated users                   |

With only `require_admin()`, what happens? You start creating:

```
require_admin()
require_editor()
require_support()
require_moderator()
require_admin_or_support()
require_admin_or_editor()
require_admin_or_moderator()
```

Very quickly you end up with dozens of authorization functions. **This doesn't scale.**

---

## Intuition

Think about a hotel.

Instead of hiring a different security guard for every room — one for the gym, one for the pool, one for the restaurant, one for the VIP lounge — **you hire one guard**.

You simply hand him a list:

```
Allowed:
VIP
Gold
Platinum
```

Tomorrow the list changes. The guard doesn't. Only the allowed list changes.

That's exactly what we'll build.

---

## From Fixed Dependencies to Configurable Dependencies

Instead of:

```python
def require_admin():
```

we want:

```python
require_roles("admin")
```

or

```python
require_roles("admin", "moderator")
```

or

```python
require_roles("admin", "support")
```

The authorization logic is written **once**.

---

## The Challenge

At first glance, you might try:

```python
def require_roles(
    *roles: str,
    current_user: User = Depends(get_current_user),
):
```

Unfortunately, this doesn't work with FastAPI.

**Why?** Because FastAPI resolves dependencies when the application starts, not when a request is handled. It cannot simultaneously treat `roles` as configuration and `current_user` as an injected dependency in the way you expect.

---

## The Solution — Dependency Factory

Instead of returning a `User`, we'll return another dependency function.

This is a **higher-order function** (remember when you learned them in Python?).

```
require_roles()
     ↓
   returns
     ↓
  dependency()
     ↓
FastAPI executes dependency()
```

### Visual Flow

```
Router
   ↓
require_roles("admin")
   ↓
creates dependency
   ↓
Request arrives
   ↓
dependency()
   ↓
get_current_user()
   ↓
Role Check
   ↓
Return User
```

---

## Implementation

Create this in `services/dependencies.py`:

```python
from collections.abc import Callable

from fastapi import Depends

from app.exceptions.auth import ForbiddenError
from app.models.user import User


def require_roles(*roles: str) -> Callable[..., User]:
    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:

        if current_user.role not in roles:
            raise ForbiddenError()

        return current_user

    return dependency
```

### Let's Break It Down

**Step 1**

```python
def require_roles(*roles: str):
```

When FastAPI starts:

```python
Depends(require_roles("admin"))
```

`roles` becomes `("admin",)`.

For:

```python
Depends(require_roles("admin", "moderator"))
```

it becomes `("admin", "moderator")`.

**Step 2**

We create another function:

```python
def dependency(...):
```

This function is what FastAPI actually executes during a request.

**Step 3**

FastAPI injects `current_user` exactly like before.

**Step 4**

Role check:

```python
if current_user.role not in roles:
```

Notice the beauty here — no matter how many roles your system has, **the code never changes**. Only the configuration changes.

---

## Using It

**Admin only:**

```python
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_roles("admin")),
):
    ...
```

**Admin or Moderator:**

```python
current_user: User = Depends(
    require_roles("admin", "moderator")
)
```

**Admin or Support:**

```python
current_user: User = Depends(
    require_roles("admin", "support")
)
```

No new authorization functions.

---

## Why Keep `require_admin()`?

You may ask: *"We already have `require_roles("admin")`. Why keep `require_admin()`?"*

A common production approach is:

```python
def require_admin():
    return require_roles("admin")
```

or simply stop using `require_admin()` altogether and replace its usages with:

```python
Depends(require_roles("admin"))
```

**Recommendation:** the second approach. It avoids duplicate code and keeps your authorization API small.

---

## Real-World Usage

Imagine GitHub's repository roles: `Read`, `Write`, `Maintain`, `Admin`.

A route might require `Maintain` **or** `Admin`. The authorization system isn't rewritten — the allowed roles are simply configured for that endpoint.

The same idea appears in many frameworks and authorization libraries.

---

## Best Practices

- Write authorization logic once and reuse it.
- Prefer configurable dependencies over creating dozens of specialized functions.
- Return the authenticated `User` after authorization succeeds.
- Keep authorization separate from business logic.

---

## Common Mistakes

### Creating One Function Per Role

```
require_admin()
require_editor()
require_support()
require_manager()
```

This doesn't scale.

### Hardcoding Checks Inside Routers

```python
if current_user.role != "admin":
```

Repeated everywhere.

### Returning `bool`

Always return the `User` so downstream code can use it.

---

## Interview Questions

1. Why is `require_roles()` more scalable than `require_admin()`?
2. What is a dependency factory in FastAPI?
3. Why does `require_roles()` return another function?
4. How does FastAPI execute the inner dependency?
5. When would you still use a dedicated `require_admin()` wrapper?

---

## Practice

Implement this yourself:

1. Replace `require_admin()` with the generic `require_roles()`.
2. Protect your existing admin-only route using:
   ```python
   Depends(require_roles("admin"))
   ```
3. Create another test role in your database, for example `moderator`.
4. Add a temporary endpoint that allows both admins and moderators:
   ```python
   Depends(require_roles("admin", "moderator"))
   ```
5. Test:
   - User → `403`
   - Moderator → Success
   - Admin → Success

---

## Senior Engineer Note

This design solves role-based authorization, but it still has a limitation.

Consider this endpoint:

```
PATCH /users/5
```

Should a regular user be able to edit their own profile? **Yes.**

Should they be able to edit someone else's profile? **No.**

This decision isn't based solely on roles — it's based on **who owns the resource**.

That's our next major evolution:

> **Lesson 38 — Resource-Based (Ownership) Authorization**, where we'll implement rules like:
> - Admins can edit any user.
> - Regular users can edit only their own profile.
> - Authorization depends on both the user's role **and** the specific resource being accessed.

This is how production systems move beyond simple RBAC into real-world authorization.