from fastapi import APIRouter

router = APIRouter()


@router.get('/')
async def get_comments():
    pass


@router.post('/')
async def new_comments():
    pass


@router.patch('/{id}')
async def update_comment():
    pass
