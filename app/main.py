from typing import Union

from fastapi import Depends, FastAPI
from .dependencies import get_query_token
from .routers import users

app = FastAPI(dependencies=[Depends(get_query_token)])
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}