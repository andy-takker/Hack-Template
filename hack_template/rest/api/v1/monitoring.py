import logging
from http import HTTPStatus

from aiomisc import timeout
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from hack_template.rest.overrides import GetSessionFactory

log = logging.getLogger(__name__)

router = APIRouter(tags=["monitoring"], prefix="/monitoring")

TSessionFactory = async_sessionmaker[AsyncSession]


class PingResponse(BaseModel):
    db: bool


@router.get(
    "/ping/",
    responses={
        HTTPStatus.INTERNAL_SERVER_ERROR: {
            "model": PingResponse,
            "description": "Ping service error",
        }
    },
)
async def ping(
    response: Response,
    session_factory: TSessionFactory = Depends(GetSessionFactory),
) -> PingResponse:
    try:
        db = await _ping(session_factory)
    except TimeoutError:
        db = False

    deps = {
        "db": db,
    }
    if all(deps.values()):
        status_code = HTTPStatus.OK
    else:
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    response.status_code = status_code
    return PingResponse(**deps)


@timeout(1)
async def _ping(session_factory: TSessionFactory) -> bool:
    try:
        async with session_factory() as session:
            await session.execute(text("select 1"))
            return True
    except (SQLAlchemyError, ConnectionRefusedError):
        log.exception("Failed to connect to database")
        return False
