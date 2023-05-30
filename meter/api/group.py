from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def new_group():
    pass


@router.get("/")
async def get_groups():
    pass


@router.patch("/{id}")
async def update_group():
    pass
