from http import HTTPMethod

from fastapi.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


def get_cors_middleware() -> Middleware:
    return Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=[
            HTTPMethod.OPTIONS,
            HTTPMethod.GET,
            HTTPMethod.HEAD,
            HTTPMethod.POST,
            HTTPMethod.DELETE,
        ],
        allow_headers=["*"],
    )
