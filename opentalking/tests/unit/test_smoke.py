from __future__ import annotations

from pathlib import Path

import opentalking.models
from opentalking.avatar.manifest import parse_manifest
from opentalking.avatar.validator import validate_avatar_dir
from opentalking.providers.synthesis import list_available_synthesis


FIXTURE_AVATARS = Path(__file__).resolve().parents[1] / "fixtures" / "avatars"


def test_list_models() -> None:
    keys = list_available_synthesis()
    assert "wav2lip" in keys
    assert "musetalk" in keys
    assert "flashtalk" in keys
    assert "fasterliveportrait" in keys
    assert "flashhead" in keys
    assert "quicktalk" in opentalking.models.list_models()


def test_wav2lip_fixture_avatar_valid() -> None:
    demo = FIXTURE_AVATARS / "singer"
    errs = validate_avatar_dir(demo)
    assert errs == []


def test_flashhead_fixture_avatar_valid() -> None:
    demo = FIXTURE_AVATARS / "anchor"
    errs = validate_avatar_dir(demo)
    assert errs == []


def test_parse_wav2lip_fixture_manifest() -> None:
    m = parse_manifest(FIXTURE_AVATARS / "singer" / "manifest.json")
    assert m.id == "singer"
    assert m.model_type == "wav2lip"


def test_anime_handsome_guy_avatar_valid() -> None:
    demo = FIXTURE_AVATARS / "anime-handsome-guy"
    errs = validate_avatar_dir(demo)
    assert errs == []


def test_ancient_beauty_avatar_valid() -> None:
    demo = FIXTURE_AVATARS / "ancient-beauty"
    errs = validate_avatar_dir(demo)
    assert errs == []


def test_laozi_avatar_valid() -> None:
    demo = FIXTURE_AVATARS / "laozi"
    errs = validate_avatar_dir(demo)
    assert errs == []


def test_office_woman_avatar_valid() -> None:
    demo = FIXTURE_AVATARS / "office-woman"
    errs = validate_avatar_dir(demo)
    assert errs == []
