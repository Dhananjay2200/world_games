"""
Test script for NVIDIA NIM / LLM connectivity.
"""

import asyncio
from app.llm import check_llm_connection, get_chat_llm
from app.config import get_settings


async def test_nim():
    settings = get_settings()
    print("=" * 65)
    print(" WorldGames AI - NVIDIA NIM LLM Diagnostic")
    print("=" * 65)
    print(f"[*] Base URL: {settings.NVIDIA_BASE_URL}")
    print(f"[*] Model:    {settings.NVIDIA_MODEL_NAME}")
    print(f"[*] API Key:  {settings.NVIDIA_API_KEY[:10]}... (len {len(settings.NVIDIA_API_KEY)})")
    
    result = await check_llm_connection()
    print(f"[*] Result:   {result}")
    
    if result.get("status") == "ok":
        print("[+] NVIDIA NIM Connection verified successfully!")
    else:
        print(f"[-] Connection issue: {result.get('message')}")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(test_nim())
