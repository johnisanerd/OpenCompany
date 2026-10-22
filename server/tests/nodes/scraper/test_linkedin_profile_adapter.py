"""Offline fixture for the optional LinkedIn profile adapter.

This file does not call Apify. The live run is recorded outside the test.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "nodes"
    / "scraper"
    / "apify_actor"
    / "linkedin_profile.py"
)
_SPEC = importlib.util.spec_from_file_location("linkedin_profile_adapter", _MODULE_PATH)
assert _SPEC and _SPEC.loader
adapter = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(adapter)

# Field names from the 2026-10-22 run of johnvc/linkedin-profile-api.
# Values are empty. The run record does not store profile or contact data.
_PROFILE_ITEM = {
    "result_type": "profile",
    "name": "",
    "firstName": "",
    "lastName": "",
    "headline": "",
    "about": "",
    "location": "",
    "countryCode": "",
    "currentCompany": "",
    "currentTitle": "",
    "experience": [],
    "pastCompanies": [],
    "education": [],
    "followers": None,
    "connections": None,
    "connectionsText": "",
    "avatar": "",
    "linkedinId": "",
    "memberId": "",
    "publicUrl": "",
    "positions": [],
    "email": None,
    "summary": "",
    "fetched_at": "",
    "fromCache": False,
    "viaUnblocker": False,
}


def test_default_actor_and_preset_stay_in_place():
    assert adapter.resolve_profile_actor(adapter.SKILL_PROFILE_ACTOR, "") == adapter.SKILL_PROFILE_ACTOR
    assert adapter.resolve_profile_actor(adapter.NODE_PRESET_ACTOR, adapter.OPTIONAL_PROFILE_ACTOR) == adapter.NODE_PRESET_ACTOR
    assert adapter.resolve_profile_actor("apify/instagram-scraper", adapter.OPTIONAL_PROFILE_ACTOR) == "apify/instagram-scraper"


def test_opt_in_maps_profile_urls_and_accepts_a_profile_row():
    actor_id = adapter.resolve_profile_actor(adapter.SKILL_PROFILE_ACTOR, adapter.OPTIONAL_PROFILE_ACTOR)
    assert actor_id == adapter.OPTIONAL_PROFILE_ACTOR
    mapped = adapter.map_profile_run_input(
        {
            "profileUrl": "https://www.linkedin.com/in/example",
            "startUrls": [{"url": "https://www.linkedin.com/in/example-two"}],
            "maxItems": 1,
        }
    )
    assert mapped == {
        "profileUrls": [
            "https://www.linkedin.com/in/example",
            "https://www.linkedin.com/in/example-two",
        ]
    }
    accepted = adapter.accept_profile_items([_PROFILE_ITEM, {"result_type": "error"}])
    assert accepted == [_PROFILE_ITEM]
    assert accepted[0]["email"] is None
    assert accepted[0]["result_type"] == "profile"
