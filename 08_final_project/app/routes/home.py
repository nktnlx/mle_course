from fastapi import APIRouter


home_route = APIRouter()

@home_route.get('/', tags=['Home'])
async def index() -> str:
    return 'Welcome to Cardiovascular Disease Prediction Platform!'