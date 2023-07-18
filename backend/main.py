import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.connect_client import Client

load_dotenv()
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/iframe_details")
async def iframe_details(tier_account_id: str = None):
    if tier_account_id is None:
        tier_account_id = os.getenv("TIER_ACCOUNT_ID")
    client = Client(
        api_key=os.getenv("API_KEY"),
        api_host=os.getenv("API_HOST"),
        tier_account_id=tier_account_id,
    )
    return await client.get_iframe_details()


app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="SPA")
