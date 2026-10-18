from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, commute, match, units

app = FastAPI(title="Live Here Before You Buy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(units.router)
app.include_router(match.router)
app.include_router(chat.router)
app.include_router(commute.router)


@app.get("/health")
def health():
    return {"status": "ok"}
