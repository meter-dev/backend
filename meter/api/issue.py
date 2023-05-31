from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_issues():
    pass


@router.get("/{id}")
async def get_issue():
    pass


@router.post("/")
async def new_issue():
    pass


@router.patch("/{id}")
async def update_issue(id: str):
    pass
