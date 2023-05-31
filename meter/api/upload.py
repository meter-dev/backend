from fastapi import APIRouter

router = APIRouter()


@router.get("/{id}")
async def get_file():
    pass


@router.post("/")
async def new_file():
    pass
