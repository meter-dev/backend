from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_metrics():
    pass


@router.post("/")
async def write_metrics():
    pass
