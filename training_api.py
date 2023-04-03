from fastapi import FastAPI, Header, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import uvicorn
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from untrained_core_function import untrained

app = FastAPI()

class Item(BaseModel):
    rowid: int
    retrain:bool
    IsApproved:bool



origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "https://localhost:44307",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# async def catch_exceptions_middleware(request: Request, call_next):
#     try:
#         return await call_next(request)
#     except Exception:
#         # you probably want some kind of logging here
#         return Response("Internal server error blah blah blah", status_code=500)

# app.middleware('http')(catch_exceptions_middleware)

@app.post("/")
async def training(item:Item):
    item_dict = item.dict()
    train = untrained(item.rowid,item.retrain,item.IsApproved)
    if train:
        responsevar = 'Success'
    else:
        responsevar = 'Failed'
    return responsevar

