from fastapi import FastAPI

app = FastAPI()

data_store = {}


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/store/{item_id}")
def store_item(item_id: int, item_value: str):
    data_store[item_id] = item_value
    return {"item_id": item_id, "value": item_value}


@app.get("/retrieve/{item_id}")
def retrieve_item(item_id: int):
    return {"item_id": item_id, "value": data_store.get(item_id)}
