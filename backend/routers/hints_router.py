import asyncio
import traceback
from fastapi import APIRouter, HTTPException
from models.schemas import GenerateHintsRequest

router = APIRouter(tags=["hints"])


@router.post("/api/hints/generate")
async def generate_hints(body: GenerateHintsRequest):
    """根据当前对话上下文，调用 DeepSeek V4 Flash 实时生成句型提示和核心词汇。
    返回: {"patterns": [...], "vocabulary": [...]}
    """
    try:
        from services.ai_service import generate_sentence_hints

        loop = asyncio.get_running_loop()
        result = await asyncio.wait_for(
            loop.run_in_executor(
                None,
                generate_sentence_hints,
                body.scene,
                body.scene_choice,
                [m.model_dump() for m in body.messages],
            ),
            timeout=45.0,
        )
        return result
    except asyncio.TimeoutError:
        print("[HINTS GENERATE ERROR] Overall timeout after 45s")
        raise HTTPException(status_code=500, detail="句型提示生成超时，请稍后重试")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[HINTS GENERATE ERROR] {type(e).__name__}: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"句型提示生成失败: {type(e).__name__}: {e}")
