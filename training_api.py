from fastapi import FastAPI, Header, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import uvicorn
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from core_function_final import corefc

app = FastAPI()

class Item(BaseModel):
    path: str
    vname:str



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
    allow_methods=["POST"],
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
async def extraction(item:Item):
    item_dict = item.dict()
    extract = corefc(item.path,item.vname)
    if extract:
        responsevar = 'Success'
    else:
        responsevar = 'Failed'
    return extract
