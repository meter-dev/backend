from fastapi import APIRouter, Path

router = APIRouter()


@router.get('/')
async def get_comments():
    pass


@router.post('/')
async def new_comments():
    pass
