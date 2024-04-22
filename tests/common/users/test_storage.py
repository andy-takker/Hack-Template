import pytest
from dirty_equals import IsList, IsPartialDict

from hack_template.common.models.pagination import MetaPaginationModel
from hack_template.common.users.base import UserType
from hack_template.common.users.models import UserModel, UserPaginationModel
from hack_template.common.users.storage import UsersStats, UserStorage


async def test_create_user__ok(user_storage: UserStorage, read_user):
    user = await user_storage.create(
        username="user",
        password_hash="top-secret",
        properties={},
    )
    assert user == await read_user(user.id)


async def test_get_by_id_user__not_exist(user_storage: UserStorage):
    assert await user_storage.get_by_id(user_id=0) is None


async def test_get_by_id_other_user_type_not_exist(
    user_storage: UserStorage, create_user
):
    user = await create_user()
    assert (
        await user_storage.get_by_id(user_id=user.id, user_type=UserType.ADMIN) is None
    )


async def test_get_by_id_user__ok(user_storage: UserStorage, create_user):
    user = await create_user()
    assert await user_storage.get_by_id(
        user_id=user.id, user_type=user.type
    ) == UserModel.model_validate(user)


async def test_get_by_username_user__not_exist(user_storage: UserStorage):
    assert await user_storage.get_by_username(username="unknown_user") is None


async def test_get_by_username_user__ok(user_storage: UserStorage, create_user):
    user = await create_user()
    assert await user_storage.get_by_username(
        username=user.username,
    ) == UserModel.model_validate(user)


@pytest.mark.parametrize(
    ("username", "password_hash"),
    (
        ("username-invalid", "secret"),
        ("username", "password-invalid"),
    ),
)
async def test_get_by_username_and_password_hash__not_exists(
    user_storage: UserStorage,
    create_user,
    username: str,
    password_hash: str,
):
    await create_user()
    assert (
        await user_storage.get_by_username_and_password_hash(
            username=username,
            password_hash=password_hash,
        )
        is None
    )


async def test_get_by_username_and_password_hash__ok(
    user_storage: UserStorage,
    create_user,
):
    user = await create_user()
    assert await user_storage.get_by_username_and_password_hash(
        username=user.username,
        password_hash=user.password_hash,
    ) == UserModel.model_validate(user)


@pytest.mark.parametrize(
    ("limit", "offset", "user_type"),
    (
        (0, 0, UserType.REGULAR),
        (0, 17, UserType.ADMIN),
        (3, 0, UserType.REGULAR),
        (15, 32, UserType.ADMIN),
    ),
)
async def test_pagination_empty_users_ok(
    user_storage: UserStorage,
    limit: int,
    offset: int,
    user_type: UserType,
):
    pagination = await user_storage.pagination(
        limit=limit,
        offset=offset,
        user_type=user_type,
    )
    assert pagination == UserPaginationModel(
        meta=MetaPaginationModel(total=0, limit=limit, offset=offset),
        items=[],
    )


async def test_pagination__format_ok(
    user_storage: UserStorage,
    create_user,
):
    user = await create_user(type=UserType.REGULAR)
    pagination = await user_storage.pagination(
        user_type=None,
        limit=10,
        offset=0,
    )
    assert pagination.model_dump() == {
        "meta": {
            "total": 1,
            "limit": 10,
            "offset": 0,
        },
        "items": [
            {
                "id": user.id,
                "type": user.type,
                "username": user.username,
            }
        ],
    }


async def test_pagination__users_regular_ok(
    user_storage: UserStorage,
    create_user,
):
    await create_user(type=UserType.REGULAR)
    await create_user(type=UserType.REGULAR)
    pagination = await user_storage.pagination(
        user_type=UserType.REGULAR,
        limit=10,
        offset=0,
    )
    assert pagination.model_dump() == IsPartialDict(
        {
            "meta": IsPartialDict(
                {
                    "total": 2,
                }
            ),
            "items": IsList(length=2),
        }
    )


async def test_pagination__users_admin_ok(
    user_storage: UserStorage,
    create_user,
):
    await create_user(type=UserType.ADMIN)
    await create_user(type=UserType.ADMIN)
    pagination = await user_storage.pagination(
        user_type=UserType.ADMIN,
        limit=10,
        offset=0,
    )
    assert pagination.model_dump() == IsPartialDict(
        {
            "meta": IsPartialDict(
                {
                    "total": 2,
                }
            ),
            "items": IsList(length=2),
        }
    )


@pytest.mark.parametrize(("limit", "result"), ((0, 0), (3, 3), (5, 3)))
async def test_pagination__limit(
    user_storage: UserStorage, create_user, limit: int, result: int
):
    await create_user()
    await create_user()
    await create_user()

    pagination = await user_storage.pagination(
        limit=limit,
        offset=0,
        user_type=None,
    )
    assert pagination.model_dump() == IsPartialDict({"items": IsList(length=result)})


@pytest.mark.parametrize(("offset", "result"), ((0, 5), (3, 2), (5, 0)))
async def test_pagination__offset(
    user_storage: UserStorage, create_user, offset: int, result: int
):
    await create_user()
    await create_user()
    await create_user()
    await create_user()
    await create_user()

    pagination = await user_storage.pagination(
        limit=5,
        offset=offset,
        user_type=None,
    )
    assert pagination.model_dump() == IsPartialDict({"items": IsList(length=result)})


async def test_pagination__offset_limit(user_storage: UserStorage, create_user):
    await create_user()
    await create_user()
    await create_user()
    await create_user()
    await create_user()

    pagination = await user_storage.pagination(
        limit=2,
        offset=2,
        user_type=None,
    )
    assert pagination.model_dump() == IsPartialDict(
        {
            "meta": {
                "total": 5,
                "limit": 2,
                "offset": 2,
            },
            "items": IsList(length=2),
        }
    )


async def test_update_by_id__new_data_empty__ok(user_storage: UserStorage, create_user):
    user = await create_user()
    updated_user = await user_storage.update_by_id(user_id=user.id, new_data={})
    assert updated_user == UserModel.model_validate(user)


async def test_update_by_id__user_not_found__ok(user_storage: UserStorage):
    assert await user_storage.update_by_id(user_id=-1, new_data={}) is None


async def test_update_by_id__new_data_ok(
    user_storage: UserStorage, create_user, read_user
):
    user = await create_user()
    updated_user = await user_storage.update_by_id(
        user_id=user.id, new_data={"age": 23}
    )
    assert updated_user == await read_user(user.id)


async def test_get_users_stats__empty_ok(user_storage: UserStorage):
    assert await user_storage.get_users_stats() == UsersStats(
        admins_count=0, regulars_count=0
    )


async def test_get_users_stats__ok(user_storage: UserStorage, create_user):
    await create_user(type=UserType.ADMIN)
    await create_user(type=UserType.REGULAR)
    assert await user_storage.get_users_stats() == UsersStats(
        admins_count=1, regulars_count=1
    )
