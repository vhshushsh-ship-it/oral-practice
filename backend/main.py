from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chat_router import router as chat_router
from routers.translate_router import router as translate_router
from routers.word_router import router as word_router
from routers.notes_router import router as notes_router
from routers.tts_router import router as tts_router
from routers.listening_router import router as listening_router
from db import init_db
from db.seed import seed_listening_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_listening_data()
    yield


app = FastAPI(title="SceneTalk Backend", lifespan=lifespan)

# CORS 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "null",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router)
app.include_router(translate_router)
app.include_router(word_router)
app.include_router(notes_router)
app.include_router(tts_router)
app.include_router(listening_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
