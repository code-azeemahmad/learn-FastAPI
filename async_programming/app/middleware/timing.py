from time import perf_counter

from fastapi import Request


async def process_time_middleware(
    request: Request,
    call_next,
):
    start = perf_counter()

    response = await call_next(request)

    process_time = perf_counter() - start

    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response