from fastapi import APIRouter

router = APIRouter()


@router.post('/token')
async def create_access_token():
    pass
