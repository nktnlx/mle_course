from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes.home import home_route
from routes.user import user_route
from routes.balance import balance_route
from routes.transaction import transaction_route
from routes.ml_task import prediction_route
from database.database import init_db
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(home_route)
app.include_router(user_route, prefix='/user')
app.include_router(balance_route)
app.include_router(transaction_route)
app.include_router(prediction_route)

if __name__ == '__main__':
    uvicorn.run('api:app', host='0.0.0.0', port=8080, reload=True)