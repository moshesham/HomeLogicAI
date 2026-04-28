from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from anthropic import AsyncAnthropic
from fastapi import HTTPException, status

from core.config import settings

_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
_PROMPTS_DIR = Path(__file__).resolve().parents[2] / "prompts"


def _load_prompt(prompt_file: str, fallback: str) -> str:
    prompt_path = _PROMPTS_DIR / prompt_file
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8")
    return fallback


async def _complete(system_prompt: str, user_content: str) -> str:
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Anthropic API key is not configured",
        )

    response = await _client.messages.create(
        model="claude-3-5-sonnet-latest",
        max_tokens=900,
        system=system_prompt,
        messages=[{"role": "user", "content": user_content}],
    )
    return "\n".join(block.text for block in response.content if getattr(block, "text", None)).strip()


async def generate_buyer_guide(category_slug: str, category_schema: dict[str, Any]) -> str:
    system_prompt = _load_prompt(
        "buyer-guide.txt",
        "Generate a practical buyer guide for the requested category.",
    )
    user_content = json.dumps(
        {"category_slug": category_slug, "category_schema": category_schema},
        ensure_ascii=False,
        indent=2,
    )
    return await _complete(system_prompt, user_content)


async def summarize_product_specs(product: dict[str, Any], category_schema: dict[str, Any]) -> str:
    system_prompt = _load_prompt(
        "spec-summary.txt",
        "Summarize product specs into plain language and buying implications.",
    )
    user_content = json.dumps(
        {"product": product, "category_schema": category_schema},
        ensure_ascii=False,
        indent=2,
    )
    return await _complete(system_prompt, user_content)


async def generate_comparison_summary(
    products: list[dict[str, Any]],
    category_schema: dict[str, Any],
) -> str:
    system_prompt = _load_prompt(
        "comparison-summary.txt",
        "Compare the provided products and provide a decision-oriented summary.",
    )
    user_content = json.dumps(
        {"products": products, "category_schema": category_schema},
        ensure_ascii=False,
        indent=2,
    )
    return await _complete(system_prompt, user_content)


async def answer_category_question(
    question: str,
    category_schema: dict[str, Any],
    products: list[dict[str, Any]],
) -> str:
    system_prompt = _load_prompt(
        "qa-assistant.txt",
        "Answer user questions about category products clearly and concisely.",
    )
    user_content = json.dumps(
        {
            "question": question,
            "category_schema": category_schema,
            "products": products,
        },
        ensure_ascii=False,
        indent=2,
    )
    return await _complete(system_prompt, user_content)
