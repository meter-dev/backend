from fastapi import APIRouter

router = APIRouter()


@router.post('/')
async def new_alert_rule():
    pass


@router.get('/')
async def get_alert_rules():
    pass


@router.get('/{id}')
async def get_alert_rule():
    pass


@router.post('/{id}/subscribe')
async def subscribe_alert_rule():
    pass


@router.post('/{id}/trigger')
async def trigger_alert():
    pass
