from fastapi import APIRouter

from common.enums import Tags

router = APIRouter()
router.tags.append(Tags.USERS)


@router.get("/users/")
async def read_users():
    return [{"username": "Foo"}, {"username": "Bar"}]


@router.get("/users/me")
async def read_user_me():
    return {"username": "fakecurrentuser"}


@router.get("/users/{username}")
async def read_user(username: str):
    return {"username": username}
