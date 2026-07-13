# Resource-Based (Ownership) Authorization

**Authentication** answers: *Who are you?*
**RBAC** answers: *What roles do you have?*
**Ownership** answers: *Does this resource belong to you?*

This is where authorization becomes much more interesting.

---

## 1. Intuition

Imagine you're using Google Drive. There are three users: **Azeem**, **Ali**, **Sarah**. Each uploads files.

```
Azeem
 ├── resume.pdf
 └── notes.pdf

Ali
 ├── invoice.pdf

Sarah
 ├── thesis.pdf
```

Now Azeem requests:

```
DELETE /files/3
```

File 3 belongs to Sarah. Should Azeem be allowed? **No.**

Even though:

- Azeem is authenticated ✅
- Azeem has role = `user` ✅

He still cannot delete Sarah's file. **Why? Because he doesn't own it.**

---

## RBAC Isn't Enough

Suppose we only have RBAC. Role = `user`. Can every user edit every profile?

```
PATCH /users/5
```

Imagine:

```
Azeem  id = 1
Ali    id = 2
```

Azeem sends:

```
PATCH /users/2
```

If your route only checks `Depends(require_roles("user"))`, then **Azeem can modify Ali**. Huge security problem.

---

## The Missing Piece

We need another check.

```
Authenticated?
     ↓
    Yes
     ↓
Role Allowed?
     ↓
    Yes
     ↓
Owns Resource?
     ↓
    Yes
     ↓
  Execute
```

Notice there are now **three gates**.

---

## 2. Real-World Examples

### Facebook

```
PATCH /posts/15
```

You can edit *your own* post. Not someone else's post.

### GitHub

```
DELETE /repositories/5
```

You cannot delete repositories you don't own unless you're an organization admin.

### Banking

```
GET /accounts/18
```

You cannot see another customer's bank account.

### ChatGPT

Imagine conversations — you should only access conversations that belong to your account. Ownership authorization protects that.

---

## 3. Types of Authorization

So far we've learned:

```
Authentication → Identity
```

Then:

```
Role-Based → Admin? Moderator?
```

Now:

```
Resource-Based → Is this YOUR resource?
```

Large applications combine all three.

---

## 4. Our Example

Current endpoint:

```
PATCH /users/{user_id}
```

We want this rule:

| Role  | Can update own profile | Can update others |
|-------|--------------------------|----------------------|
| User    | ✅                          | ❌                     |
| Admin    | ✅                          | ✅                      |

This is extremely common.

### Visual

```
PATCH /users/5
      ↓
Current User = id=5
      ↓
Requested User = id=5
      ↓
    Allowed
```

Another request:

```
PATCH /users/8
      ↓
Current User = id=5
      ↓
Requested User = id=8
      ↓
   Forbidden
```

Admin:

```
PATCH /users/8
      ↓
Current User = Admin
      ↓
    Allowed
```

---

## 5. Where Should This Logic Live?

Beginners often write:

```python
if current_user.id != user_id:
    raise HTTPException(...)
```

inside every router. **Don't.** That duplicates logic again — we already learned this lesson with roles.

### Better Architecture

We'll build another dependency.

```
get_current_user()
       ↓
require_owner_or_admin()
       ↓
     Router
```

Notice how we keep stacking reusable dependencies.

---

## 6. The Challenge

Unlike `require_roles()`, ownership checks need something extra: **the path parameter**.

Example:

```
PATCH /users/5
```

We need:

```
Current User → id = 3
     AND
Requested User ID → 5
```

Both are required.

### Visual

```
Request
   ↓
JWT
   ↓
Current User
   ↓
Path Parameter
   ↓
Compare IDs
   ↓
Allow / Deny
```

This is our first authorization rule that depends on **request data**, not just the authenticated user.

---

## 7. Building `require_owner_or_admin()`

In `services/dependencies.py`:

```python
from fastapi import Depends

from app.exceptions.auth import ForbiddenError
from app.models.user import User


def require_owner_or_admin(
    user_id: int,
    current_user: User = Depends(get_current_user),
) -> User:

    if current_user.role == "admin":
        return current_user

    if current_user.id != user_id:
        raise ForbiddenError()

    return current_user
```

Read it like English:

```
If admin
   ↓
Always allow

Else
   ↓
Is requested user ID mine?
   ↓
  Yes → Allow
   ↓
  Else → 403
```

---

## 8. Using It

Our route becomes:

```python
@router.patch("/{user_id}")
def update_user(
    user_id: int,
    request: UserPatch,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_owner_or_admin),
):
    return service.patch(user_id, request)
```

Notice something fascinating — FastAPI automatically injects:

- `user_id` from the URL
- `current_user` from the JWT

into the **same** dependency. That's one of FastAPI's most powerful features.

---

## 9. Test Cases

### User edits own profile

```
JWT → id=5
PATCH /users/5
     ↓
  Allowed
```

### User edits another profile

```
JWT → id=5
PATCH /users/8
     ↓
    403
```

### Admin edits another profile

```
JWT → Admin
PATCH /users/8
     ↓
  Allowed
```

Perfect.

---

## 10. Why This Doesn't Belong in the Service

You might ask: *"Why not put this in `UserService.patch()`?"*

Good question. Remember our architecture:

```
Router → Dependencies → Service → Repository
```

The service should focus on business operations: updating user data, validating business rules, coordinating repositories.

Authorization based on the current HTTP request belongs **at the edge** of the application — in dependencies — so the service only runs after access has been approved.

> In larger systems, some business-level authorization does move into services, especially when operations can be triggered outside HTTP (CLI tools, background jobs, message queues). We'll discuss that distinction later.

---

## 11. Best Practices

- Keep ownership checks reusable.
- Combine role checks and ownership checks instead of duplicating them.
- Let FastAPI inject both path parameters and the authenticated user.
- Return the `User` object after successful authorization.

---

## 12. Common Mistakes

### Hardcoding Ownership Checks

```python
if current_user.id != user_id:
```

inside every router.

### Forgetting the Admin Bypass

Without:

```python
if current_user.role == "admin":
```

admins couldn't manage other users.

### Comparing the Wrong IDs

Always compare the authenticated user's ID with the resource owner's ID or the target resource identifier, depending on your authorization rule.

---

## 13. Interview Questions

1. What's the difference between RBAC and resource-based authorization?
2. Why isn't RBAC alone sufficient for applications like social media or banking?
3. How does FastAPI inject both path parameters and dependencies into the same function?
4. Why should admins bypass ownership checks?
5. Where should ownership authorization live in a layered FastAPI application?

---

## 14. Practice

Implement the following:

1. Add `require_owner_or_admin()` to `services/dependencies.py`.
2. Protect your `PATCH /users/{user_id}` endpoint with it.
3. Test these scenarios:
   - User updates their own profile → `200 OK`
   - User updates another user's profile → `403 Forbidden`
   - Admin updates another user's profile → `200 OK`
4. Verify that your service and repository code do not need any authorization logic — they should work unchanged because the dependency enforces access before they are called.

---

## A Small Design Improvement

Your current dependency compares against a `user_id` path parameter. That works well for user endpoints.

As your application grows, you'll have resources like:

```
/posts/{post_id}
/orders/{order_id}
/comments/{comment_id}
```

Those require checking the owner of the *resource*, not just comparing IDs from the URL. In those cases, the dependency typically loads the resource first (or calls a repository) and compares its `owner_id` with `current_user.id`.

We'll build that more advanced pattern when we introduce relationships and richer domain models like `User → Posts`. That's the approach you'll see in production systems.