# Intro to JWT

> Why JWT Exists, and the Anatomy of a JWT

---

## Part 1 — Why JWT Exists

### 1. Intuition

Imagine you're going to a hotel.

You check in. The receptionist verifies:

- Your identity
- Your booking
- Your payment

After verification, they hand you a **room key**.

Now imagine every time you wanted to enter your room, you had to go back to the receptionist and prove your identity again. Ridiculous.

Instead:

```
Check In
   ↓
Receive Room Key
   ↓
Use Room Key
```

The receptionist doesn't verify you every single time — the room key proves you've already been verified.

**Authentication on the web works the same way.**

---

### 2. The Problem

Suppose you have your current application.

```
POST /auth/login
```

```json
{
    "email": "azeem@gmail.com",
    "password": "password123"
}
```

The server verifies your password. Everything is fine.

Then one second later:

```
GET /users
```

How does the server know it's you? The request only contains `GET /users`. No email. No password. No identity.

**Why? Because HTTP is stateless.**

---

### 3. What Does Stateless Mean?

Every HTTP request is independent.

```
Request 1 → Server → Response
```

Finished. Later:

```
Request 2 → Server
```

The server has no memory of Request 1.

Think of sending physical letters. Each envelope arrives independently — the post office doesn't remember the last envelope you sent. HTTP behaves similarly.

---

### 4. The First Solution — Sessions

Before JWT existed, most applications used **sessions**.

**Step 1 — User logs in**

```
Client → POST /login → Server
```

Server verifies credentials.

**Step 2 — The server creates a session**

```
Session ID: abc123xyz
```

Server stores:

```
abc123xyz → User ID = 5
```

in its database or memory.

**Step 3 — Server sends only the session ID back**

```
Set-Cookie: session_id=abc123xyz
```

The browser stores it automatically.

**Step 4 — Every future request includes the cookie**

```
Cookie: session_id=abc123xyz
```

The server receives `abc123xyz`, looks it up:

```
Session Table
abc123xyz → User 5
```

Now it knows who you are.

#### Visual

```
Login
  ↓
Create Session
  ↓
Store Session
  ↓
Return Cookie
  ↓
Future Requests
  ↓
Lookup Session
  ↓
Identify User
```

Simple.

---

### 5. What's Wrong with Sessions?

Nothing — sessions still power many applications. But they don't scale well. Let's see why.

**Imagine one server**

```
Client → Server A
```

Session lives here. Everything works.

**Now imagine 100,000 users**

You add another server.

```
        Client
        /     \
  Server A   Server B
```

Login happens on Server A. Session stored:

```
Server A: abc123 → User 5
```

Later:

```
GET /users
```

Request reaches Server B. Server B asks: *"What's abc123?"* It doesn't know — the session exists only on Server A.

**The user appears logged out.**

---

### 6. Possible Solutions

**Option 1 — Sticky Sessions**

Always send the user back to Server A. Problem: not ideal — load balancing becomes harder.

**Option 2 — Move sessions into Redis**

```
Server A → Redis ← Server B
```

Now every server queries Redis. Works well, still common today. But now every authenticated request requires:

```
Request → Redis Lookup → Continue
```

That's an extra network call every time.

---

### 7. The JWT Idea

Instead of storing authentication state on the server... **store it in the token.**

The server says: "Here's a signed token." The client stores it. Every request sends it back. The server verifies the signature. Done.

No database lookup required just to identify the user.

#### Visual

```
Login
  ↓
Generate JWT
  ↓
Client Stores JWT
  ↓
Future Request
  ↓
Authorization: Bearer <JWT>
  ↓
Verify Signature
  ↓
Read User ID
  ↓
Continue
```

The server doesn't need a session table. That's why we call JWT authentication **stateless**.

---

### 8. Stateless vs Stateful

**Sessions**

```
Client → Session ID → Server → Session Store → User
```

The server stores state. This is **stateful**.

**JWT**

```
Client → JWT → Server → Verify Signature → User
```

The server doesn't store login state. This is **stateless**.

---

### 9. Does JWT Eliminate the Database?

**No.** This is a very common misconception.

The JWT may tell us:

```json
{ "sub": "5" }
```

Now we know `User ID = 5`. But what if we need name, role, email, or permissions? We still fetch the user from the database when needed.

> JWT removes the need for a session **lookup**, not the need for your application's **data**.

---

### 10. Why Is JWT So Popular?

Because it works beautifully with:

- REST APIs
- Mobile apps
- Single Page Applications (React, Vue, Angular)
- Microservices
- Cloud-native deployments

This is why nearly every modern API uses it.

---

### 11. Best Practices

- Understand JWT as a way to carry verified identity, not as encrypted data.
- Don't put sensitive information (like passwords) inside tokens.
- Keep access tokens short-lived.
- Use HTTPS so tokens aren't exposed in transit.
- Validate the token's signature on every protected request.

---

### 12. Common Misconceptions

| Misconception | Reality |
|---|---|
| ❌ "JWT is encrypted." | The payload is typically just Base64URL encoded, which anyone can decode. Integrity comes from the **signature**, not secrecy. |
| ❌ "JWT replaces the database." | It replaces the need for a session lookup, not your application's persistent data. |
| ❌ "JWT is always better than sessions." | Many server-rendered applications still use sessions successfully. The right choice depends on architecture and requirements. |

---

### 13. Interview Questions

1. What does it mean for HTTP to be stateless?
2. How do sessions authenticate users?
3. What problem do sticky sessions try to solve?
4. Why do distributed systems make session management more complex?
5. What does JWT replace in a typical authentication flow?
6. Does JWT eliminate the need for a database?
7. Is JWT encrypted by default?
8. Why are JWTs popular for REST APIs?

---

### Revision — Part 1

**Key Concepts**

- HTTP is stateless.
- Sessions store authentication state on the server.
- JWT stores authenticated identity inside a signed token.
- JWT avoids server-side session storage for authentication.
- The database is still used for application data.

**Visual Summary**

```
Sessions                      JWT

Client                        Client
  │                             │
Session ID                  Bearer Token
  │                             │
Server                        Server
  │                             │
Session Store              Verify Signature
  │                             │
User                     User ID (from token)
                                │
                          Database (when needed)
```

---
---

## Part 2 — Anatomy of a JWT (JSON Web Token)

> After this section, you'll never look at a JWT as just a long random string again — you'll be able to read it, decode it, and understand exactly what every part means.

### 1. Intuition

Imagine you're traveling internationally. You have a passport containing:

- Who you are
- Your nationality
- Passport number
- Expiry date

When you reach immigration, they don't call your home country to ask "Is this really Azeem?" Instead, they verify the passport format, issuing authority, security features, and expiration. If everything checks out, you're allowed in.

**A JWT works almost exactly the same way.**

---

### 2. What is a JWT?

**JWT** stands for **JSON Web Token**.

It is a compact string that contains **claims** (pieces of information) about a user, along with a **cryptographic signature** that proves the token hasn't been tampered with.

JWTs are not random strings — they're highly structured.

---

### 3. What Does a JWT Look Like?

A real JWT looks like this:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.
eyJzdWIiOiIxIiwiZXhwIjoxNzYwMDAwMDAwLCJpYXQiOjE3NTk5OTAwMDB9
.
QjQ5X5B7J8N2xwP2...
```

Notice the dots — there are always three parts:

```
Header . Payload . Signature
```

Every JWT follows this format.

#### Visual

```
┌──────────┐
│ Header   │
└──────────┘
      .
┌──────────┐
│ Payload  │
└──────────┘
      .
┌──────────┐
│Signature │
└──────────┘
```

---

### 4. Part 1 — Header

The first section tells us how the token was signed.

Decoded, it looks like:

```json
{
    "alg": "HS256",
    "typ": "JWT"
}
```

Meaning: **Algorithm → HS256** and **Token Type → JWT**.

**What is HS256?**

HS256 means **HMAC + SHA-256** — the algorithm used to create the signature.

You don't need to know the cryptography yet. Just remember: it is how the server proves the token hasn't been modified.

---

### 5. Part 2 — Payload

The payload contains **claims** — pieces of information.

```json
{
    "sub": "15",
    "email": "azeem@gmail.com",
    "role": "admin",
    "exp": 1760000000,
    "iat": 1759990000
}
```

Notice — this is just JSON.

---

### 6. Common Claims

| Claim | Name | Meaning |
|---|---|---|
| `sub` | Subject | Usually the user's unique identifier, e.g. `"sub": "15"` → User ID = 15 |
| `exp` | Expiration Time | Unix timestamp; after this time the token is invalid |
| `iat` | Issued At | When the token was created |
| `nbf` | Not Before | The token is not valid before this time (advanced scenarios) |
| `iss` | Issuer | Who created the token |
| `aud` | Audience | Who the token is intended for — useful when multiple apps consume the same auth service |

---

### 7. Custom Claims

You can also add your own:

```json
{
    "sub": "15",
    "role": "admin",
    "department": "AI"
}
```

These are called **private claims**.

**Should We Store Everything? No.**

Never put sensitive information inside a JWT.

Bad:

```json
{ "password": "mypassword" }
```

Very bad. Also avoid:

- Credit card numbers
- Social Security numbers
- API keys
- Secrets

Remember: the payload is usually readable.

---

### 8. Part 3 — Signature

This is the **most important** part. The signature proves nobody modified the token.

Conceptually:

```
Header + Payload + Secret Key
           ↓
         HS256
           ↓
       Signature
```

The server creates the signature using its secret key. When a request arrives, the server recalculates the signature.

- If the signatures match → the token is authentic.
- If not → reject it.

#### Visual

```
Header
  ↓
Payload
  ↓
Secret Key
  ↓
HS256
  ↓
Signature
```

The secret key **never leaves the server**.

---

### 9. What Happens if Someone Changes the Payload?

Suppose an attacker changes:

```json
{ "role": "user" }
```

to:

```json
{ "role": "admin" }
```

The payload changes, but the signature doesn't. The server computes a new signature and compares it:

```
Client Signature ≠ Server Signature
```

Result: **401 Unauthorized** — the token is rejected.

---

### 10. JWT Is Signed, Not Encrypted

This is one of the biggest misconceptions.

Anyone can decode the Header and Payload. But no one can create a valid signature without the server's secret key.

Think of it like a **wax seal on a letter**. Anyone can read the letter if they have it, but only the sender can create the authentic seal.

---

### 11. Where Is the JWT Stored?

Commonly, for SPAs (like a React frontend), the client stores the token (the exact storage mechanism depends on the application's security design).

Then every request includes:

```
Authorization: Bearer <JWT>
```

Example:

```
GET /users/me
Authorization: Bearer eyJhbGciOi...
```

The server extracts the token from the `Authorization` header and verifies it.

---

### 12. Best Practices

- Keep the payload small.
- Use `sub` for the user identifier.
- Set a reasonable expiration (`exp`).
- Never include secrets in the payload.
- Protect your signing secret.
- Always verify the signature before trusting the claims.

---

### 13. Common Errors

| Error | Explanation |
|---|---|
| ❌ Thinking Base64 encoding is encryption | Encoding makes data portable, not secret. |
| ❌ Storing passwords in the token | Passwords should never leave the database. |
| ❌ Forgetting expiration | Tokens without expiration can remain valid indefinitely if leaked. |
| ❌ Trusting claims without verifying the signature | A decoded token is meaningless unless its signature has been validated. |

---

### 14. Interview Questions

1. What are the three parts of a JWT?
2. What information belongs in the header?
3. What is a claim?
4. What does the `sub` claim represent?
5. Why is the `exp` claim important?
6. What is the purpose of the signature?
7. Is JWT encrypted by default?
8. Can anyone read the payload?
9. What happens if someone modifies the payload?
10. Why must the server keep its signing secret private?

---

### 15. Practice

Without looking at your notes, answer:

1. Why are there exactly three sections in a JWT?
2. Why is the payload readable?
3. What does the signature protect?
4. Why can't an attacker simply change `"role": "user"` to `"role": "admin"`?
5. Which claim would you use to identify the logged-in user?

---

### Revision — Part 2

**JWT Structure**

```
Header
  .
Payload
  .
Signature
```

**Header**

```json
{
    "alg": "HS256",
    "typ": "JWT"
}
```

**Payload**

```json
{
    "sub": "15",
    "exp": "...",
    "iat": "...",
    "role": "admin"
}
```

**Signature**

```
HS256(
    Header +
    Payload +
    Secret Key
)
```

---

## Mentor's Note

One thing to refine from the previous lesson: it was said the server doesn't need a database lookup after verifying a JWT. That's only partially true.

A JWT tells you who the user *claims* to be, and a valid signature proves the token was issued by your server. But many production systems still fetch the user from the database (or a cache) after validating the token to ensure the account still exists, check current roles, or verify the account hasn't been disabled.

> Think of the JWT as an **identity credential**, not a replacement for your application's data.

---

## Next Lesson

**Access Tokens** → generating and issuing real JWTs in the signup/login flow.