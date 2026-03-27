"""Gemini API 클라이언트 — 사주 상담 응답 생성"""

import os
import asyncio
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

# .env 로드 (프로젝트 루트)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = "gemini-2.0-flash"


def _configure():
    if not API_KEY:
        raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    genai.configure(api_key=API_KEY)


def _build_messages(system_prompt: str, user_message: str, chat_history: list | None = None) -> list[dict]:
    """Gemini contents 형식으로 변환"""
    contents = []
    if chat_history:
        for h in chat_history:
            role = h.get("role", "user")
            text = h.get("message", h.get("content", ""))
            if role in ("user", "assistant") and text:
                contents.append({
                    "role": "model" if role == "assistant" else "user",
                    "parts": [{"text": text}],
                })
    contents.append({"role": "user", "parts": [{"text": user_message}]})
    return contents


async def generate(
    system_prompt: str,
    user_message: str,
    chat_history: list | None = None,
) -> str:
    """Gemini API 비동기 호출 — 전체 응답 (대화형)"""
    return await asyncio.to_thread(
        _generate_sync, system_prompt, user_message, chat_history, 4000, 0.8
    )


async def generate_intro(
    system_prompt: str,
    intro_prompt: str,
) -> str:
    """Gemini API 비동기 호출 — 짧은 개인화 인트로 (2-3문장)"""
    return await asyncio.to_thread(
        _generate_sync, system_prompt, intro_prompt, None, 300, 0.9
    )


def _generate_sync(
    system_prompt: str,
    user_message: str,
    chat_history: list | None = None,
    max_tokens: int = 4000,
    temperature: float = 0.8,
) -> str:
    """Gemini API 동기 호출"""
    _configure()
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=system_prompt,
        generation_config=genai.GenerationConfig(
            temperature=temperature,
            top_p=0.9,
            max_output_tokens=max_tokens,
        ),
    )
    contents = _build_messages(system_prompt, user_message, chat_history)
    response = model.generate_content(contents)
    return response.text.strip()
