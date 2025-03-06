from fastapi import APIRouter

router = APIRouter(
    prefix="/config",
    tags=["config"],
)


@router.get("/")
def config_endpoint():
    return {"endpoint": "config"}
