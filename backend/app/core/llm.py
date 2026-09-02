import httpx
from app.core.config import settings


async def summarize_texts(texts: list[str], question: str) -> str | None:
    """Summarize a batch of free-text survey answers into 2-3 sentences.

    Returns None if no API key is configured or the call fails, so callers
    can fall back to a non-LLM summary instead of failing the request.
    """
    if not settings.ANTHROPIC_API_KEY or not texts:
        return None

    joined = "\n".join(f"- {t.strip()}" for t in texts[:200] if t.strip())
    if not joined:
        return None

    prompt = (
        f'Survey question: "{question}"\n\n'
        f"Here are respondent answers:\n{joined}\n\n"
        "In 2-3 short sentences, summarize the key themes, common sentiment, "
        "and any notable impact described above. Be concise and specific."
    )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": settings.ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": settings.ANTHROPIC_MODEL,
                    "max_tokens": 220,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            parts = data.get("content", [])
            text = "".join(p.get("text", "") for p in parts).strip()
            return text or None
    except Exception:
        return None
