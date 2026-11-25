"""
LLM Provider and Factory Configuration for WorldGames AI.
Modular abstraction for NVIDIA NIM and OpenAI-compatible endpoints using LangChain.
"""

from typing import Optional
from langchain_openai import ChatOpenAI
from app.config import get_settings
from app.utils.logging import logger


def get_chat_llm(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: Optional[int] = None,
) -> ChatOpenAI:
    """
    Factory function to instantiate the configured Chat LLM.
    Defaults to NVIDIA NIM via OpenAI-compatible API specifications.
    """
    settings = get_settings()

    selected_model = model_name or settings.NVIDIA_MODEL_NAME
    selected_temp = temperature if temperature is not None else settings.LLM_TEMPERATURE
    selected_tokens = max_tokens or settings.LLM_MAX_TOKENS
    selected_timeout = timeout or settings.LLM_TIMEOUT

    logger.debug(
        f"Initializing ChatOpenAI instance: model={selected_model}, "
        f"base_url={settings.NVIDIA_BASE_URL}, temp={selected_temp}"
    )

    return ChatOpenAI(
        model=selected_model,
        api_key=settings.NVIDIA_API_KEY,
        base_url=settings.NVIDIA_BASE_URL,
        temperature=selected_temp,
        max_tokens=selected_tokens,
        timeout=selected_timeout,
        max_retries=2,
    )


async def check_llm_connection() -> dict:
    """
    Tests connectivity to the NVIDIA NIM endpoint by sending a minimal test prompt.
    Returns status, latency in milliseconds, and the sample response.
    """
    import time

    settings = get_settings()

    if not settings.NVIDIA_API_KEY or settings.NVIDIA_API_KEY.startswith("nvapi-placeholder"):
        return {
            "status": "warning",
            "message": "NVIDIA_API_KEY is not configured or using default placeholder. Please set your key in .env file.",
            "latency_ms": 0,
        }

    try:
        llm = get_chat_llm(max_tokens=20, temperature=0.1)
        start_time = time.time()
        response = await llm.ainvoke("Respond with single word: 'Ready'")
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "ok",
            "model": settings.NVIDIA_MODEL_NAME,
            "response": response.content.strip(),
            "latency_ms": latency_ms,
        }
    except Exception as e:
        logger.error(f"NVIDIA NIM connection check failed: {e}")
        return {
            "status": "error",
            "model": settings.NVIDIA_MODEL_NAME,
            "message": str(e),
            "latency_ms": 0,
        }
