from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query, Response, Security

from hack_template.utils.auth.base import AUTH_COOKIE
from hack_template.utils.auth.models import AuthTokenModel, AuthUser
from hack_template.utils.rest.models import StatusResponse
from hack_template.utils.rest.overrides import (
    REQUIRE_ADMIN_AUTH,
    REQUIRE_AUTH,
    GetUserDispatcher,
    GetUserStorage,
)
from hack_template.utils.users.base import UserType
from hack_template.utils.users.dispatcher import UserDispatcher
from hack_template.utils.users.models import (
    CreateUserModel,
    LoginUserModel,
    UpdateUserModel,
    UserModel,
    UserPaginationModel,
)
from hack_template.utils.users.storage import UserStorage

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/",
    responses={
        200: {"model": UserPaginationModel},
        403: {
            "model": StatusResponse,
            "description": "Forbidden",
        },
    },
)
async def get_users(
    limit: int = Query(default=10, gt=0, le=100),
    offset: int = Query(default=0, gt=-1),
    user_storage: UserStorage = Depends(GetUserStorage),
    auth_user: AuthUser = Security(REQUIRE_AUTH),
) -> UserPaginationModel:
    if auth_user.type == UserType.ADMIN:
        user_type = None
    else:
        user_type = UserType.REGULAR
    return await user_storage.pagination(
        limit=limit,
        offset=offset,
        user_type=user_type,
    )


@router.post(
    "/",
    dependencies=[Security(REQUIRE_ADMIN_AUTH)],
)
async def create_user(
    new_user: CreateUserModel,
    response: Response,
    user_dispatcher: UserDispatcher = Depends(GetUserDispatcher),
) -> AuthTokenModel:
    auth_token = await user_dispatcher.create(new_user=new_user)
    response.set_cookie(AUTH_COOKIE, auth_token.token)
    return auth_token


@router.get(
    "/{user_id}/",
    dependencies=[Security(REQUIRE_AUTH)],
    responses={
        HTTPStatus.OK: {"model": UserModel},
        HTTPStatus.NOT_FOUND: {
            "model": StatusResponse,
            "description": "User not found",
        },
        HTTPStatus.FORBIDDEN: {
            "model": StatusResponse,
            "description": "Forbidden",
        },
    },
)
async def get_user(
    user_id: int,
    user_storage: UserStorage = Depends(GetUserStorage),
) -> UserModel:
    user = await user_storage.read_by_id(user_id=user_id)
    if user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


@router.post(
    "/{user_id}/",
    responses={
        HTTPStatus.OK: {"model": UserModel},
        HTTPStatus.BAD_REQUEST: {
            "model": StatusResponse,
            "description": "No data to update",
        },
        HTTPStatus.FORBIDDEN: {"model": StatusResponse, "description": "Forbidden"},
        HTTPStatus.NOT_FOUND: {
            "model": StatusResponse,
            "description": "User not found",
        },
    },
)
async def update_user(
    user_id: int,
    update_user: UpdateUserModel,
    auth_user: AuthUser = Security(REQUIRE_AUTH),
    user_storage: UserStorage = Depends(GetUserStorage),
) -> UserModel:
    if auth_user.id != user_id and auth_user.type != UserType.ADMIN:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="Forbidden")
    new_data = update_user.model_dump()
    if not new_data:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="No data to update"
        )
    user = await user_storage.update_by_id(
        user_id=user_id,
        new_data=new_data,
    )
    if user is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")
    return user


@router.post(
    "/login/",
    responses={
        HTTPStatus.OK: {"model": AuthTokenModel},
        HTTPStatus.BAD_REQUEST: {
            "model": StatusResponse,
            "description": "Username or password is incorrect",
        },
    },
)
async def login(
    login_user: LoginUserModel,
    user_dispatcher: UserDispatcher = Depends(GetUserDispatcher),
) -> AuthTokenModel:
    auth_token = await user_dispatcher.login(login_user=login_user)
    if auth_token is None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Username or password is incorrect",
        )
    return auth_token
