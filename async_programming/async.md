# Module 8 — Asynchronous Programming in FastAPI

> Lesson 1 — Why Do We Need `async`? · Lesson 2 — Coroutines and the Event Loop · Lesson 3 — When to Use `def` vs `async def`

Most tutorials teach async as:

```python
async def get_users():
    ...
```

and

```python
await database.fetch(...)
```

without explaining why. This module builds the mental model first — once you understand it, every async framework (FastAPI, Node.js, C#, Rust Tokio, Go goroutines) becomes much easier to learn.

---
---

## Lesson 1 — Why Do We Need `async`?

Before we write any code, answer this question: **why did Python invent async?**

The answer is **not** "to make programs faster." That's one of the biggest misconceptions.

### 1. Imagine a Restaurant

#### Restaurant A (Synchronous)

There is one waiter. Customers arrive: Customer 1, 2, 3, 4.

The waiter does this:

```
Take Order
   ↓
Walk to Kitchen
   ↓
Stand there waiting...
   ↓
Food Ready
   ↓
Deliver Food
   ↓
Go to Customer 2
```

While the kitchen is cooking, **the waiter is doing nothing** — just waiting.

```
Customer 1 → Take order → WAIT 10 minutes → Deliver
Customer 2 → WAIT
Customer 3 → ...
```

Everyone waits.

### 2. But Who Is Actually Working?

The waiter isn't cooking — the kitchen is. The waiter is simply waiting for the kitchen. That's wasted time.

### 3. Restaurant B (Asynchronous)

Same waiter, different strategy. Instead of waiting after taking Order 1, the waiter immediately goes to Customer 2, then 3, then 4.

```
Take Order 1
   ↓
Take Order 2
   ↓
Take Order 3
   ↓
Take Order 4
   ↓
Kitchen finishes Order 1 → Serve
   ↓
Kitchen finishes Order 2 → Serve
```

**The waiter never stands idle.**

### This Is Concurrency

The waiter is not cooking four meals simultaneously. There is still one waiter, one kitchen. He simply doesn't waste time waiting.

### 4. How Does This Relate to FastAPI?

```python
@app.get("/users")
def get_users():
    users = database.query(...)
    return users
```

```
Request
   ↓
Database Query
   ↓
WAIT
   ↓
Database Responds
   ↓
Return JSON
```

During that wait, your CPU isn't doing database work — PostgreSQL is. Your Python process is simply waiting.

### 5. Another Example

```python
requests.get(...)
```

Your code sends a request, then waits. Who is working? The remote server. **Python is idle.**

### Waiting Is Everywhere

Backend applications constantly wait for: Database, Redis, File system, HTTP APIs, AI models, Email servers, Cloud storage. The CPU is idle most of the time.

### 6. Synchronous Execution

Three users hit your API:

```
A ======>
B ======>
C ======>

Total: 3 × database time
```

Request B only starts after Request A finishes entirely.

### 7. Asynchronous Execution

```
A → Database → Waiting
```

Instead of sitting idle, Python starts `B → Database`, then `C → Database`.

```
A =====>
B =====>
C =====>
```

All three are waiting at roughly the same time. When each finishes, Python resumes handling it.

> **Important:** Python is not making PostgreSQL faster. Python is simply not wasting time waiting. This distinction is critical.

### 8. CPU Work vs I/O Work

This is **the single most important concept** in async programming.

**CPU-bound work** — Image processing, video encoding, ML training, encryption, compression. The CPU is busy. **Async does not make this faster.**

**I/O-bound work** — Database queries, HTTP requests, reading files, Redis, email, S3, LLM API calls. The CPU mostly waits. **Async shines here.**

```
CPU-bound:                    I/O-bound:

Python                        Python
██████████████████            ██  Waiting...  ██  Waiting...  ██
Working                       Most of the timeline is waiting.
```

Async uses that waiting time.

### 9. A Common Myth

People say *"async is faster."* Not exactly. More precisely:

> Async improves **throughput** by reducing idle waiting during I/O operations.

A single request might even take nearly the same amount of time. The benefit is that your server can handle many waiting requests efficiently.

### 10. When Should We Use Async?

**Good candidates:** database queries (async driver), external APIs, Redis, file uploads/downloads, AI inference services, streaming responses, WebSockets.

**Not good candidates:** sorting a huge list in memory, image processing, ML training, heavy mathematical computations.

### 11. FastAPI and Async

FastAPI was designed around asynchronous programming, letting you write:

```python
@app.get("/users")
async def get_users():
    ...
```

But: **just writing `async def` doesn't automatically make your code asynchronous.** If you call blocking code inside it, you'll still block the event loop (explored in Lesson 2/3).

### Mental Model

Synchronous code: `Start Task → Wait → Continue`

Async code: `Start Task → Pause While Waiting → Let Someone Else Run → Resume When Ready`

`await` essentially says: *"I'm waiting for an I/O operation. While I'm waiting, go work on something else. Come back when this operation completes."*

### Interview Questions

1. Why was async introduced?
2. What's the difference between CPU-bound and I/O-bound work?
3. Does async make code run faster?
4. What kinds of operations benefit most from async?
5. Explain asynchronous programming using a real-world analogy.

### Practice — Classify as CPU-bound or I/O-bound

| Task | CPU-bound or I/O-bound? |
|---|---|
| Query PostgreSQL | ? |
| Read a file from disk | ? |
| Send an email | ? |
| Resize a 4K image | ? |
| Train a neural network | ? |
| Call the OpenAI API | ? |
| Calculate Fibonacci(45) | ? |
| Download a PDF | ? |

---
---

## Lesson 2 — Coroutines and the Event Loop

> Almost every beginner thinks *"async makes code run in the background."* That's not true. By the end of this lesson, you'll understand what coroutines, `await`, and the event loop actually are.

### 1. First, Forget FastAPI

```python
def greet():
    print("Hello")

greet()
```

```
Program → greet() → Print Hello → Return
```

The function starts immediately.

### 2. Now Change One Word

```python
async def greet():
    print("Hello")
```

Many beginners think this behaves the same. It doesn't.

**Question:** What happens here?

```python
async def greet():
    print("Hello")

greet()
```

Will it print? Most beginners answer *yes*. **Wrong.** It prints nothing. Instead:

```
RuntimeWarning: coroutine 'greet' was never awaited
```

### 3. What Does `async def` Return?

A normal function returns its value:

```python
def add():
    return 5

x = add()  # x = 5
```

An async function is different:

```python
async def add():
    return 5

x = add()  # x = Coroutine Object, not 5
```

#### Intuition

Think of a coroutine as a **recipe**. Reading the recipe doesn't bake the cake — it simply tells you how to bake it. A coroutine describes work that *can* happen. It doesn't execute by itself.

```
Normal function:              Async function:

Call Function                 Call Function
   ↓                             ↓
Runs Immediately              Create Coroutine
                                  ↓
                                Wait
```

Nothing executes yet.

### 4. Who Executes Coroutines?

This is where the **Event Loop** enters.

Imagine a factory — workers don't start working until a manager assigns tasks.

```
Worker → Waiting → Manager Gives Task → Work Starts
```

**The manager is the Event Loop.**

The event loop is a scheduler. Its job: start, pause, resume, and finish coroutines. It keeps track of thousands of coroutines.

```
Event Loop
   ├── Coroutine A
   ├── Coroutine B
   ├── Coroutine C
   └── Coroutine D
```

The event loop decides which coroutine runs next.

### 5. What Does `await` Mean?

```python
async def fetch_data():
    ...

await fetch_data()
```

People often read this as simply "wait" — that's only half the story. A better interpretation:

> Pause this coroutine until `fetch_data()` finishes. While paused, let the event loop run something else.

```
Coroutine A → await Database → PAUSE
```

While A is paused, the event loop starts Coroutine B. Later, when the database is ready, Coroutine A resumes.

### 6. Restaurant Analogy Revisited

```
Waiter → Kitchen → Order Cooking → Serve Another Customer
   → Kitchen Rings Bell → Return
```

The waiter didn't disappear — he switched tasks. **The event loop is managing that switching.**

### 7. Multiple Coroutines

```python
async def task_a(): ...
async def task_b(): ...
async def task_c(): ...
```

The event loop might execute them like:

```
Task A → Waiting → Task B → Waiting → Task C → Waiting
   → Resume A → Resume B → Resume C
```

No operating system thread switching. No extra CPUs. Just **cooperative scheduling**.

### 8. Cooperative Multitasking

This phrase appears in interviews. Python async uses cooperative multitasking because a coroutine voluntarily says `await something`, meaning *"I'm waiting. Someone else can run now."* Nobody interrupts it — it cooperates.

Compare with threads: threads are interrupted by the operating system. **Coroutines pause themselves.**

### 9. Event Loop Timeline

```python
await database()
await redis()
await email()
```

```
Start
   ↓
Database Waiting → Run Another Coroutine → Database Ready
   ↓
Redis Waiting → Run Another Coroutine → Redis Ready
   ↓
Email Waiting → Run Another Coroutine → Done
```

The CPU never sits idle.

### 10. Does `await` Create a New Thread?

**No.** One of the biggest misconceptions. `await` does **not** create a thread, process, or CPU core. It simply tells the event loop: *pause here.* That's it.

### 11. FastAPI and the Event Loop

```python
@app.get("/users")
async def get_users():
    ...
```

FastAPI doesn't call it directly. Instead, the ASGI server (typically Uvicorn) submits the coroutine to the event loop, which schedules its execution.

```
HTTP Request → Uvicorn → Event Loop → Coroutine → Response
```

### 12. The Big Picture

```
Client
   ↓
Uvicorn
   ↓
Event Loop
   ↓
Coroutine
   ↓
await Database
   ↓
Coroutine Paused
   ↓
Run Another Request
   ↓
Database Finishes
   ↓
Resume Original Coroutine
   ↓
Return Response
```

This is the core of asynchronous web servers.

### Mental Model

- `async def` → *"This function may pause."*
- `await` → *"Pause here while waiting. Let another coroutine run."*
- Event loop → *"The scheduler that decides which coroutine runs next."*

### Common Misconceptions

| Misconception | Reality |
|---|---|
| ❌ `async` starts immediately | It creates a coroutine object. |
| ❌ `await` creates a thread | It pauses the coroutine. |
| ❌ `async` always makes code faster | It mainly improves concurrency for I/O-bound work. |
| ❌ Coroutines run in parallel | A single event loop runs one coroutine at a time, switching between them whenever they `await`. |

### Interview Questions

1. What is a coroutine?
2. What does `async def` return?
3. What is the role of the event loop?
4. What does `await` actually do?
5. Why is Python async called cooperative multitasking?
6. Does `await` create a new thread?

### Practice (No Coding Yet)

1. Will `"Hello"` be printed by `async def hello(): print("Hello"); hello()`?
2. What object is returned by `x = hello()`?
3. Who is responsible for executing that coroutine?
4. What does `await` tell the event loop?

---
---

## Lesson 3 — When to Use `def` vs `async def`

> Many developers get this wrong by following a simple rule like "always use async." The correct answer is more nuanced.

### The Rule

The decision is **not** based on FastAPI — it's based on what your function does.

**Ask yourself:** Does this function perform asynchronous I/O?

```
Does this function call asynchronous code?
            │
      ┌─────┴─────┐
     Yes          No
      │           │
 async def       def
```

### Applying It to Your Project

**Layer 1 — Routers**

```python
@router.get("/")
def get_users(
    service: UserService = Depends(get_user_service),
):
    return service.get_users()
```

Should this become `async def`? **Not yet.** It calls `service.get_users()`, which is synchronous, which calls `repository.get_all()`, which uses synchronous SQLAlchemy. The entire call chain is synchronous — making only the router async gains nothing.

**Layer 2 — Services**

```python
class UserService:
    def get_users(self):
        return self.repository.get_all()
```

Should it be async? **No** — it performs no asynchronous work; it just delegates to synchronous repository methods.

**Layer 3 — Repository**

```python
def get_all(self):
    return self.db.query(User).all()
```

This uses synchronous SQLAlchemy `Session` and blocks until PostgreSQL responds. `def` is correct.

**Why Not Write `async def` Anyway?**

```python
async def get_users():
    return self.repository.get_all()
```

Looks asynchronous — isn't. Inside you're still calling blocking code:

```
Coroutine → Blocking SQL Query → Event Loop Waits
```

You've actually **blocked the event loop**. This is one of the biggest beginner mistakes.

**What Makes Code Truly Async?**

Instead of `Session`, you'd use `AsyncSession`. Instead of `.query(...)`, you'd use `await session.execute(...)`. Only then does the coroutine pause instead of blocking. (Covered in the next lesson.)

**Layer 4 — Password Hashing**

```python
password_hasher.hash(password)
```

Should this be async? **No.** Hashing is CPU work — nothing to await. Remember: **CPU work ≠ async.**

**Layer 5 — JWT**

```python
jwt.encode(...)
jwt.decode(...)
```

CPU operations — no network, no disk, no database. `def` is correct.

**Layer 6 — Authorization Dependencies**

```python
def require_roles(...):
```

Should this become async? **Not today** — it calls `repository.get_by_id(...)`, which is synchronous, so the dependency stays synchronous.

**Layer 7 — Middleware**

```python
async def process_time_middleware(...):
```

Why? Because `await call_next(request)` is asynchronous. Middleware interacts with the ASGI application asynchronously, so FastAPI expects async middleware.

**Layer 8 — Exception Handlers**

Usually `async def handler(...)` because FastAPI invokes them within its asynchronous request lifecycle.

### A Common Mistake

```python
async def login():
    hashed = bcrypt.hash(password)
    token = jwt.encode(...)
    return token
```

There isn't a single asynchronous operation — everything is CPU work. Using `async` here adds no benefit.

### Another Mistake

Developers think `async def` means *faster*. **No.** If there is no `await`, the event loop never gets a chance to switch to another coroutine.

### Classifying the Current Project

| Component | Current | Correct? | Reason |
|---|---|---|---|
| Routers | `def` | ✅ | Uses synchronous services |
| Services | `def` | ✅ | Uses synchronous repositories |
| Repository | `def` | ✅ | Uses `Session` |
| Password Hasher | `def` | ✅ | CPU-bound |
| JWT Service | `def` | ✅ | CPU-bound |
| Dependencies | `def` | ✅ | Uses synchronous repository |
| Middleware | `async def` | ✅ | Uses `await call_next()` |
| Exception Handlers | `async def` | ✅ | Integrated into async request handling |

**So the current architecture is correct.** You should not convert everything to async just because FastAPI supports it.

### When Will We Change to Async?

Only after switching to `AsyncEngine`, `AsyncSession`, an async PostgreSQL driver (such as `asyncpg`), and async SQLAlchemy APIs. Then the call chain becomes:

```
Router → Service → Repository → AsyncSession → PostgreSQL
```

At that point, each layer can become asynchronous.

### Real Production Example

```python
async def get_weather():
    response = await httpx.AsyncClient().get(...)
```

Correct — the HTTP request is I/O-bound and `httpx.AsyncClient` is asynchronous.

Compare:

```python
async def calculate():
    return fibonacci(45)
```

Nothing to await — this should simply be `def calculate():`.

### Mental Model

Don't ask *"Is this FastAPI?"* — ask *"Does this function await asynchronous I/O?"* That single question guides your choice.

### Best Practices

- Use `def` for synchronous code.
- Use `async def` only when you'll be awaiting asynchronous operations.
- Don't mix async functions with blocking libraries.
- Convert entire call chains to async rather than isolated functions.

### Interview Questions

1. Should every FastAPI route be `async def`?
2. Why doesn't wrapping synchronous database code in `async def` make it asynchronous?
3. Why are password hashing and JWT encoding usually synchronous?
4. What changes are required before a SQLAlchemy application can become truly asynchronous?
5. Why is middleware typically written as `async def`?

### Practice — Classify

| Function | `def` or `async def`? |
|---|---|
| `hash_password()` | ? |
| `create_access_token()` | ? |
| `send_email()` using an async mail client | ? |
| `fetch_user()` using `AsyncSession` | ? |
| `resize_image()` | ? |
| `call_openai()` using `httpx.AsyncClient` | ? |

---

## Next Lesson

**Migrating a Real FastAPI Project from Synchronous SQLAlchemy to Async SQLAlchemy**

We'll take the existing project and learn:

- `Engine` → `AsyncEngine`
- `Session` → `AsyncSession`
- `create_engine()` → `create_async_engine()`
- `.query()` → `select()`
- `commit()`, `refresh()`, `execute()`
- Dependency injection with async sessions

This is one of the most valuable skills for modern FastAPI development because it transforms the concepts learned here into a fully asynchronous application.


# Sync vs Async — What Do We Actually Gain?

The real question is: **what problem are we solving by moving from synchronous to asynchronous code?**

The answer depends on your application's workload.

---

## What Do We Gain?

### 1. Higher Concurrency (The Biggest Benefit)

Imagine your current synchronous application. Suppose each database query takes **500 ms**, and three users send requests simultaneously.

#### Synchronous

```
Request A
   │
   ├── Database (500 ms)
   │
   └── Response

Request B waits...
Request C waits...
```

**Timeline:**

```
A: ██████████
B:           ██████████
C:                     ██████████

Total time: ≈ 1500 ms
```

#### Asynchronous

```
Request A → Database
Request B → Database
Request C → Database
```

While PostgreSQL is processing all three queries, Python isn't sitting idle.

**Timeline:**

```
A: ██████████
B: ██████████
C: ██████████

Total: ≈ 500 ms
```

The database was always capable of handling multiple queries. The difference is that **your Python server stopped wasting time waiting**.

---

### 2. Better Server Throughput

Suppose your API receives **1000 requests/second**, and each request queries PostgreSQL, calls Redis, calls OpenAI, and sends an email.

Most of the request lifetime is *waiting*.

**With sync:**

```
Python
WAIT...
WAIT...
WAIT...
```

**With async:**

```
Python
While Request A waits...
   ↓
Process Request B
   ↓
Process Request C
   ↓
Resume Request A
```

One process can efficiently manage many more concurrent connections.

---

### 3. Better for AI Applications

Especially relevant to a long-term goal of becoming an AI backend engineer.

Imagine `POST /chat`:

```
Receive Prompt
   ↓
Call OpenAI API
   ↓
Wait 3 seconds
   ↓
Return Answer
```

Those 3 seconds are almost entirely network waiting.

**With sync:** worker blocked for 3 seconds.

**With async:**

```
Worker starts OpenAI request
   ↓
Handles other requests
   ↓
OpenAI responds
   ↓
Resume
```

This is exactly why AI APIs often use async HTTP clients.

---

### 4. Better Resource Utilization

Suppose your CPU usage is **15%**, but your server is slow. Why? Because the CPU isn't working — it's waiting.

Async helps utilize that idle time. It doesn't increase CPU speed — it increases **useful work done while waiting**.

---

### 5. Better Scalability

Imagine 500 concurrent users.

- With synchronous code, you often need more worker processes or threads to keep up.
- With asynchronous code, a single worker can often manage many more concurrent I/O-bound requests because it isn't blocked during waits.

That can reduce memory usage and improve scalability.

---

## What Do We NOT Gain?

This is even more important.

| Task | Why Async Doesn't Help |
|---|---|
| ❌ Faster CPU calculations (e.g. `fibonacci(45)`) | The CPU is still busy doing math. |
| ❌ Faster password hashing (`bcrypt.hash(password)`) | Still CPU work. No improvement. |
| ❌ Faster JWT encoding (`jwt.encode(...)`) | Pure CPU. No improvement. |
| ❌ Faster image processing (resize a 4K image) | Still CPU-bound. |
| ❌ Faster ML training (PyTorch / TensorFlow) | Compute-intensive. Async won't speed it up. |

---

## Does Each User Get Faster Responses?

**Not necessarily.**

Suppose a database query takes 200 ms:

```
Sync:  ≈ 200 ms
Async: ≈ 200 ms
```

The response time for that single request is often very similar. **The advantage is that while one request waits 200 ms, the server can handle many other requests.**

---

## Real Example from Your Project

Currently:

```
Login
   ↓
Query User
   ↓
Verify Password
   ↓
Generate JWT
   ↓
Return
```

Only **Query User** benefits from async. **Verify Password** and **Generate JWT** remain synchronous because they're CPU operations.

Another example:

```
Signup
   ↓
Insert User
   ↓
Commit
   ↓
Refresh User
```

These database operations benefit from async because they involve waiting for PostgreSQL.

### Example: AI Backend

Imagine `POST /chat`:

```
Receive prompt
   ↓
Save chat to PostgreSQL
   ↓
Call OpenAI
   ↓
Store response
   ↓
Return JSON
```

Waiting occurs during **PostgreSQL** and **OpenAI API** calls — excellent candidates for async. The CPU-intensive parts (like token counting or prompt formatting) remain synchronous.

---

## Should Every FastAPI Project Be Async?

**No.**

A small CRUD application used by 10 employees in an internal company dashboard may work perfectly well with synchronous SQLAlchemy. Async introduces additional concepts and complexity — choose it when the benefits outweigh that complexity.

### When Should You Stay Synchronous?

A synchronous architecture is often sufficient if:

- You have a small internal application.
- Traffic is low.
- You're using only synchronous libraries.
- Simplicity is more important than maximizing concurrency.

Many successful production applications remain synchronous for these reasons.

### When Should You Choose Async?

Async is a strong choice when your application:

- Handles many concurrent users.
- Makes lots of database queries.
- Calls external APIs frequently.
- Streams responses (e.g. AI chat).
- Uses WebSockets.
- Performs many I/O operations where waiting dominates execution time.

These are exactly the kinds of systems FastAPI excels at.

---

## For Your Career Goal

Given the goal of building AI-powered backends, RAG systems, OpenAI/Ollama integrations, streaming chat applications, and real-time systems with WebSockets — **learning and eventually using async is recommended**.

These applications spend a significant amount of time waiting on databases, vector stores, and external AI services, making asynchronous programming a valuable skill.

That said, learning the synchronous architecture first was also the right path — it's what makes the *why* behind async actually click.


# Module 8 — Async FastAPI
## Lesson 4 — Migrating from Sync SQLAlchemy to Async SQLAlchemy (Architecture)

> No coding yet. Today's goal is to understand the architecture before touching any files.

---

## 1. Why Can't We Just Write `async def`?

Suppose you change your repository:

```python
async def get_all(self):
    return self.db.query(User).all()
```

Looks async, right? **Actually, no.**

Why? Because this line:

```python
self.db.query(User).all()
```

is still using a **synchronous** database driver. The database call blocks until PostgreSQL responds. Your event loop is stuck waiting.

```
Coroutine
   ↓
Blocking SQL Query
   ↓
Event Loop Stops
```

This defeats the purpose of async.

---

## 2. What Actually Makes Database Access Async?

There are **four pieces** that must work together.

### Piece 1 — Async Driver

Today:

```
SQLAlchemy → psycopg2
```

`psycopg2` is synchronous. Instead we use an asynchronous PostgreSQL driver — examples: `asyncpg`, `psycopg` (async mode).

Now:

```
SQLAlchemy → asyncpg → PostgreSQL
```

The driver itself knows how to perform non-blocking I/O.

### Piece 2 — Async Engine

Today:

```python
engine = create_engine(...)
```

Tomorrow:

```python
engine = create_async_engine(...)
```

Think of the engine as the bridge between SQLAlchemy and PostgreSQL. A synchronous bridge can't suddenly become asynchronous — we replace the bridge.

### Piece 3 — Async Session

Today: `Session`

Tomorrow: `AsyncSession`

This session understands asynchronous database operations.

### Piece 4 — Awaitable Queries

Today:

```python
users = session.query(User).all()
```

Tomorrow:

```python
result = await session.execute(...)
```

Notice the keyword `await` — now the coroutine can pause while PostgreSQL is working.

---

## The Complete Picture

**Current:**

```
FastAPI
   ↓
Repository
   ↓
Session
   ↓
create_engine
   ↓
psycopg2
   ↓
PostgreSQL
```

**Future:**

```
FastAPI
   ↓
Repository
   ↓
AsyncSession
   ↓
create_async_engine
   ↓
asyncpg
   ↓
PostgreSQL
```

Every layer now supports asynchronous execution.

---

## 3. What Doesn't Change?

This is an important point. **Your architecture stays the same.** You still have:

```
Router → Service → Repository
```

You're not redesigning the application — you're **replacing the plumbing underneath**.

---

## 4. What Files Will Change?

Current structure:

```
app/
├── database/
│   └── database.py
├── repositories/
│   └── user_repository.py
├── services/
│   └── user_service.py
└── routers/
    └── users.py
```

Not every file changes. Let's classify them.

| File | Changes? | Why |
|---|---|---|
| `database/database.py` | ✅ Yes | Engine and session become async |
| `repositories/user_repository.py` | ✅ Yes | Queries become async |
| `services/user_service.py` | ✅ Yes | Awaits repository methods |
| `routers/users.py` | ✅ Yes | Awaits service methods |
| `schemas/` | ❌ No | Data models stay the same |
| `models/` | ❌ Almost never | ORM mappings are unchanged |
| `jwt.py` | ❌ No | CPU work |
| `security.py` | ❌ No | Password hashing is CPU work |
| `config.py` | ❌ No | Configuration is unaffected |

Notice how most of your project doesn't need to change.

---

## 5. The Async Call Chain

**Today's synchronous request:**

```
Request → Router → Service → Repository → Database → Return
```

**Tomorrow:**

```
Request
   ↓
Router
   ↓ await
Service
   ↓ await
Repository
   ↓ await
Database
   ↓
Resume
   ↓
Return
```

Every layer awaits the next one.

---

## 6. Why the Whole Chain Must Be Async

Imagine only the repository is async:

```python
async def get_all(...)
```

But the service is:

```python
def get_users():
    repository.get_all()
```

**Problem.** You can't properly call an async function from synchronous code without running the event loop yourself.

Instead:

```python
async def get_users():
    return await repository.get_all()
```

Now the chain matches.

### Visual

```
Router
   ↓ await
Service
   ↓ await
Repository
   ↓ await
Database
```

**If one link is async, the callers above it generally need to become async too.**

---

## 7. Why Models Don't Change

```python
class User(Base):
    ...
```

doesn't care whether the database connection is synchronous or asynchronous. A model simply describes table name, columns, and relationships. It isn't responsible for executing queries.

---

## 8. Why Schemas Don't Change

Pydantic doesn't know or care how data arrived — whether the user came from PostgreSQL, Redis, MongoDB, or memory, your schema is still `UserResponse`. No changes needed.

---

## 9. What About Password Hashing?

Still:

```python
password_hasher.hash(...)
```

No `await`. Hashing is CPU work — making it async wouldn't help.

---

## 10. What About JWT?

Still:

```python
jwt.encode(...)
```

Still synchronous. JWT creation is pure computation.

---

## 11. The Big Migration Plan

We're not going to change everything at once — we'll migrate **one layer at a time**.

| Step | Layer | Change |
|---|---|---|
| 1 | Database | `Engine` → `AsyncEngine` |
| 2 | Session | `Session` → `AsyncSession` |
| 3 | Repository | Replace synchronous queries |
| 4 | Services | Await repository methods |
| 5 | Routers | Await service methods |

### Mental Model

You're not rewriting your project. You're replacing the synchronous database plumbing with asynchronous plumbing. Everything above it simply learns to `await`.

---

## Best Practices

- Migrate from the bottom up (database → repository → service → router).
- Keep your architecture unchanged.
- Don't mix sync and async database APIs in the same call chain.
- Leave CPU-bound utilities (JWT, password hashing) synchronous.

---

## Interview Questions

1. Why isn't `async def` alone enough to make database code asynchronous?
2. What components are required for async SQLAlchemy?
3. Why don't ORM models need to change during migration?
4. Why do schemas remain unchanged?
5. Why should you migrate the call chain from the database upward?

---

## Before We Start Coding

There's one more concept needed before editing the project: **the difference between synchronous SQLAlchemy and asynchronous SQLAlchemy APIs.** Specifically:

- Why `.query()` disappears
- Why `select()` becomes the preferred approach
- Why `execute()` returns a `Result`
- What `.scalars()` does
- Why `.first()` and `.all()` look different in async code

Once these API differences are understood, the migration itself becomes straightforward rather than feeling like memorizing new syntax.