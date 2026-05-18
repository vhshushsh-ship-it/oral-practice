from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.chat_router import router as chat_router
from routers.translate_router import router as translate_router
from routers.word_router import router as word_router
from routers.notes_router import router as notes_router

app = FastAPI(title="SceneTalk Backend")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
