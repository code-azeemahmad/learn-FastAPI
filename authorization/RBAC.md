# Authorization: Roles & Permissions (RBAC)

**Authentication** answers *"Who are you?"*
**Authorization** answers *"What are you allowed to do?"*

These are completely different problems.

---

## 1. Intuition

Imagine you're entering an airport.

### Step 1 — Authentication

A security officer checks your passport.

```
You
 ↓
Passport
 ↓
Identity Verified ✓
```

They now know who you are.

### Step 2 — Authorization

Now imagine you try to enter the control tower. Security asks: *"Are you a pilot?"*

Even though your identity is verified, you are not authorized.

```
Authenticated
 ↓
Can enter airport        ✓
Can enter control tower  ✗
```

Authentication got you into the airport. **Authorization decides where you can go.**

---

## 2. Authentication vs Authorization

| Authentication      | Authorization           |
|----------------------|---------------------------|
| Who are you?          | What can you do?           |
| Login                 | Permission Check           |
| Email + Password      | Role + Permission           |
| JWT                    | RBAC                          |
| Happens first          | Happens after authentication |

The request flow becomes:

```
Request
   ↓
JWT
   ↓
Authenticated?
   ↓
No → 401 Unauthorized
   ↓
Yes
   ↓
Permission Check
   ↓
Allowed?
   ↓
No → 403 Forbidden
   ↓
Yes
   ↓
Execute Endpoint
```

Notice there are **two gates**, not one.

---

## 3. Why We Need Authorization

Imagine you're building a blogging platform. There are three types of users: **Guest**, **User**, **Admin**.

Should all three be allowed to delete users? Of course not.

| Action            | Guest | User | Admin |
|--------------------|-------|------|-------|
| Read posts          | ✅    | ✅   | ✅    |
| Create post          | ❌    | ✅   | ✅    |
| Edit own post         | ❌    | ✅   | ✅    |
| Delete own post        | ❌    | ✅   | ✅    |
| Delete any post          | ❌    | ❌   | ✅    |
| Delete users               | ❌    | ❌   | ✅    |

Without authorization, every authenticated user could perform every action.

---

## 4. What Is a Role?

A **role** is simply a collection of permissions.

Instead of saying "Azeem can: Read Posts, Write Posts, Delete Posts, Delete Users, Manage Payments, Manage Settings, ..." — we assign a role:

```
Role = Admin
```

The role already contains those permissions.

---

## 5. What Is a Permission?

A **permission** represents one specific capability.

Examples:

```
users:read
users:create
users:update
users:delete
posts:create
posts:delete
orders:refund
```

Permissions are much more granular than roles.

---

## 6. Role-Based Access Control (RBAC)

RBAC means:

```
User → Role → Permissions → Endpoint
```

**Example:**

```
Azeem → Admin → Delete Users → DELETE /users/5 → Allowed
```

**Another example:**

```
Ali → Regular User → Delete Users → Denied
```

---

## 7. Real-World Usage

Companies rely heavily on RBAC.

### Google

`Viewer`, `Editor`, `Owner` — different permissions for each role.

### GitHub

Repository permissions: `Read`, `Triage`, `Write`, `Maintain`, `Admin`.

### AWS IAM

Probably the most famous RBAC system. Permissions like `ec2:StartInstances`, `s3:GetObject`, `lambda:InvokeFunction` are grouped into policies and attached to users or roles.

### OpenAI

Think about the ChatGPT Team or Enterprise products. Not every member can manage billing, invite users, or delete the workspace — different roles have different capabilities.

---

## 8. How Should We Store Roles?

A beginner might think:

```python
class User(Base):
    role = "admin"
```

This works for tiny projects, but it's not flexible.

A slightly better version:

```python
role = Column(String)
```

Values: `admin`, `user`, `moderator`. Still simple, but manageable for many applications.

For larger systems, we **normalize** the data:

```
Users → Roles → Permissions
```

Tables:

```
users
roles
permissions
role_permissions
user_roles
```

This supports users with multiple roles and dynamic permission management.

---

## 9. What Will We Build?

We'll grow in stages.

**Stage 1 (next implementation)**

```
User → role → admin
```

Simple and sufficient for learning.

**Stage 2**

```
User → Role Table → Permission Table
```

**Stage 3**

```
Permission Dependency → Route Protection
```

---

## 10. Protecting an Endpoint

Today, a protected route looks like:

```python
current_user: User = Depends(get_current_user)
```

Soon, we'll add another dependency:

```python
Depends(require_admin)
```

Example:

```python
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_admin),
):
    ...
```

Read it like English: *"Only an admin may execute this route."*

No `if` statements in the router — that's the power of FastAPI's dependency injection.

---

## 11. HTTP Status Codes

Two status codes are often confused.

### 401 Unauthorized

The user is not authenticated.

Examples: no JWT, invalid JWT, expired JWT.

### 403 Forbidden

The user is authenticated but lacks permission.

Example:

```
User Role = user
   ↓
DELETE /users/5
   ↓
403 Forbidden
```

Identity is known. Access is denied.

---

## 12. Best Practices

- Authenticate first, authorize second.
- Don't hardcode permission checks inside routers.
- Centralize authorization logic in reusable dependencies.
- Keep roles simple initially; evolve to permissions as needed.
- Return `401` for authentication failures and `403` for authorization failures.

---

## 13. Common Mistakes

### Checking Roles in Every Route

Avoid:

```python
if current_user.role != "admin":
    ...
```

repeated across many routes. Instead, create reusable dependencies like `require_admin()`.

### Confusing Authentication with Authorization

A valid JWT does not automatically grant access to every endpoint.

### Hardcoding User IDs

Don't write checks like:

```python
if current_user.id == 1:
```

Roles and permissions should determine access, not specific IDs.

---

## 14. Interview Questions

1. What's the difference between authentication and authorization?
2. What is RBAC?
3. Why use roles instead of assigning permissions directly to every user?
4. When should an API return 401 vs 403?
5. Why shouldn't authorization logic live inside routers?
6. What are the limitations of storing roles as plain strings?
7. How do large systems evolve from simple roles to permissions?

---

## 15. Practice

No coding yet. Instead, design the authorization model for these applications:

- Blog platform
- E-commerce website
- Online learning platform

For each, list:

- Roles
- Permissions
- Which role can perform which actions

---

## Revision

### Authentication

*Who are you?*

### Authorization

*What are you allowed to do?*

### Request Flow

```
Request
   ↓
JWT Verification
   ↓
Authenticated?
   ↓
No → 401
   ↓
Yes
   ↓
Role / Permission Check
   ↓
Allowed?
   ↓
No → 403
   ↓
Yes
   ↓
Execute Route
```