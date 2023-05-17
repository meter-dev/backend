from fastapi import APIRouter

router = APIRouter()


@router.post('/signup')
async def signup():
    pass


@router.get('/')
async def get_users():
    pass


@router.patch('/{id}')
async def update_user(id: str):
    '''
    Update user properties
    '''
    pass


@router.post('/verify-email')
async def verify_email():
    pass
