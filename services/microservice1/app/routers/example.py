from fastapi import APIRouter

router = APIRouter(
    prefix="/example",
    tags=["example"],
)


@router.get("/")
def example_endpoint():
    return [
        {"name": "Song One"},
        {"name": "Song Two"},
        {"name": "Song Three"}
    ]
