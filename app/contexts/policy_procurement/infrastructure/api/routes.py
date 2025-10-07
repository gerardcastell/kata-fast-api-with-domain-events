from fastapi import APIRouter

router = APIRouter(
    prefix="/policy-procurement",
    tags=["policy-procurement"],
)


@router.post("/proposals")
async def create_proposal():
    return {"message": "Hello, World!"}
