from __future__ import annotations

import json
from typing import Any, Dict, List

import requests

from app.config import get_settings


def build_teams_message_card(title: str, summary: str, facts: List[Dict[str, str]], text: str, theme_color: str = "0076D7") -> Dict[str, Any]:
    return {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": summary,
        "themeColor": theme_color,
        "title": title,
        "text": text,
        "sections": [{
            "markdown": True,
            "facts": facts,
        }],
    }


def send_teams_notification(payload: Dict[str, Any] | str) -> Dict[str, Any]:
    settings = get_settings()
    webhook_url = settings.teams_webhook_url
    if not webhook_url:
        return {"sent": False, "reason": "Teams webhook not configured"}

    body = payload if isinstance(payload, dict) else {"text": payload}
    try:
        response = requests.post(webhook_url, data=json.dumps(body), headers={"Content-Type": "application/json"}, timeout=10)
        response.raise_for_status()
        return {"sent": True, "status_code": response.status_code, "payload": body}
    except Exception as exc:  # pragma: no cover - network failure path
        return {"sent": False, "reason": str(exc), "payload": body}
