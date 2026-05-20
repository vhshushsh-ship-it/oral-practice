from fastapi import APIRouter, Query
from fastapi.responses import Response
from services.tts_service import generate_tts_audio

router = APIRouter(prefix="/api", tags=["tts"])


@router.get("/tts")
async def tts(text: str = Query(..., min_length=1, max_length=500), rate: float = Query(1.0, ge=0.5, le=3.0)):
    audio_bytes = await generate_tts_audio(text, rate)
    return Response(content=audio_bytes, media_type="audio/mpeg")
