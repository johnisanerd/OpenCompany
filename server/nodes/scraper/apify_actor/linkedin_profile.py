"""Optional LinkedIn profile adapter.

The Apify skill names ``curious_coder/linkedin-profile-scraper`` for
LinkedIn profiles. The node preset ``apify/linkedin-scraper`` is a
different actor and is not changed here. Set
``OPENCOMPANY_LINKEDIN_PROFILE_ACTOR`` to
``johnvc/linkedin-profile-api`` to send that skill actor's profile URLs
as ``profileUrls`` and keep rows whose ``result_type`` is ``profile``.
"""

from __future__ import annotations

import os
from typing import Any

SKILL_PROFILE_ACTOR = "curious_coder/linkedin-profile-scraper"
OPTIONAL_PROFILE_ACTOR = "johnvc/linkedin-profile-api"
ENV_NAME = "OPENCOMPANY_LINKEDIN_PROFILE_ACTOR"
NODE_PRESET_ACTOR = "apify/linkedin-scraper"

_URL_KEYS = ("profileUrls", "profileUrl", "urls", "url", "linkedinUrl", "startUrls", "targetUrls")


def resolve_profile_actor(actor_id: str, env_value: str | None = None) -> str:
    """Return the actor id to run. The default is the id the caller asked for."""
    if env_value is None:
        env_value = os.environ.get(ENV_NAME, "")
    if actor_id == SKILL_PROFILE_ACTOR and env_value.strip() == OPTIONAL_PROFILE_ACTOR:
        return OPTIONAL_PROFILE_ACTOR
    return actor_id


def _url_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        text = value.strip()
        return [text] if text else []
    if isinstance(value, dict):
        return _url_strings(value.get("url") or value.get("linkedinUrl"))
    if isinstance(value, list):
        found: list[str] = []
        for item in value:
            found.extend(_url_strings(item))
        return found
    return []


def map_profile_run_input(actor_input: dict[str, Any]) -> dict[str, Any]:
    """Keep only profile URLs. This actor's input schema requires ``profileUrls``."""
    urls: list[str] = []
    for key in _URL_KEYS:
        urls.extend(_url_strings(actor_input.get(key)))
    deduped: list[str] = []
    for url in urls:
        if url not in deduped:
            deduped.append(url)
    return {"profileUrls": deduped[:1000]}


def accept_profile_items(items: list[Any]) -> list[dict[str, Any]]:
    """Keep profile rows. Other rows are not profile results."""
    accepted: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict) and item.get("result_type") == "profile":
            accepted.append(item)
    return accepted
