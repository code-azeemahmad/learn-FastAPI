from time import perf_counter
import logging

from fastapi import Request

logger = logging.getLogger(__name__)

async def logging_middleware(
    request: Request,
    call_next,
):
    start = perf_counter()

    response = await call_next(request)

    duration = (perf_counter() - start) * 1000

    logger.info(
        "%s %s %s %.2f ms",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    return response