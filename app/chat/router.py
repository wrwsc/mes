from fastapi import APIRouter

router = APIRouter()

@router.get("/chat")
async def get_chat():
    return {'none'}