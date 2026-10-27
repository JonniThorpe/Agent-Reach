# -*- coding: utf-8 -*-
"""Dedicated tests for the ``youtube`` channel.

YouTube's readiness is layered: yt-dlp must probe alive (missing / broken /
unrunnable are distinct), a JS runtime is mandatory (deno works out of the
box, Node needs an explicit ``--js-runtimes`` config), and transcription
readiness (whisper provider + ffmpeg/ffprobe) is surfaced for ``doctor`` without
gating the backend. These tests stub ``probe_command`` / ``shutil.which``
so every branch runs offline. Follow-up to #331 — extends dedicated
channel coverage after rss (#360), github (#361), web (#363),
reddit (#364), xueqiu (#365) and v2ex (#366).
"""

from pathlib import Path

from agent_reach.channels.youtube import YouTubeChannel


def _which(*present):
    """shutil.which side effect: returns a path for the named tools present."""
    return lambda name: f"/usr/bin/{name}" if name in present else None


# --- can_handle ---

def test_can_handle_matches_youtube_hosts():
    ch = YouTubeChannel()
    for url in [
        "https://www.youtube.com/watch?v=abc",
        "https://youtu.be/abc",
        "https://m.youtube.com/watch?v=abc",
        "https://YOUTUBE.COM/shorts/x",
    ]:
        assert ch.can_handle(url) is True, url
    for url in ["https://example.com", "https://vimeo.com/123", ""]:
        assert ch.can_handle(url) is False, url


# --- _has_js_runtime_config ---









# --- check(): yt-dlp probe states ---







# --- check(): JS runtime gating (backend stays yt-dlp once the probe is ok) ---











def test_constraints_pin_ytdlp_to_current_stable_release():
    constraints = Path(__file__).parents[1] / "constraints.txt"
    pin = next(
        line
        for line in constraints.read_text(encoding="utf-8").splitlines()
        if line.startswith("yt-dlp==")
    )

    assert pin == "yt-dlp==2026.8.19"


def test_project_installs_official_ytdlp_default_dependencies():
    root = Path(__file__).parents[1]
    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    constraints = (root / "constraints.txt").read_text(encoding="utf-8")

    assert '"yt-dlp[default]==2026.8.19"' in pyproject
    assert "yt-dlp-ejs==0.8.0" in constraints




# --- check(): transcription readiness surfaced (deno present so JS path is ok) ---









# --- subtitle track choice: one track, never a needless machine translation ---

import json  # noqa: E402
import os  # noqa: E402

import pytest  # noqa: E402

from agent_reach.channels import youtube  # noqa: E402
from agent_reach.runtime.result import ReachError  # noqa: E402

_ES = ["es", "es-ES", "es-419", "en"]


def test_pick_prefers_human_subtitles_in_a_wanted_language():
    info = {"language": "en", "subtitles": {"en": [{}], "es": [{}]}, "automatic_captions": {"en-orig": [{}], "es": [{}]}}
    assert youtube._pick_subtitle_track(info, _ES) == ("es", False, False)


def test_pick_uses_original_language_auto_captions_before_any_translation():
    # Every language shows up in automatic_captions; only the original is not a translation.
    info = {"language": "en", "subtitles": {}, "automatic_captions": {"en-orig": [{}], "en": [{}], "es": [{}], "zh-Hans": [{}]}}
    assert youtube._pick_subtitle_track(info, _ES) == ("en-orig", True, False)


def test_pick_falls_back_to_spoken_language_when_no_orig_track():
    info = {"language": "fr", "subtitles": {"live_chat": [{}]}, "automatic_captions": {"fr": [{}], "es": [{}]}}
    assert youtube._pick_subtitle_track(info, _ES) == ("fr", True, False)


def test_pick_translates_only_as_last_resort_and_reports_none():
    info = {"subtitles": {}, "automatic_captions": {"es": [{}]}}
    assert youtube._pick_subtitle_track(info, _ES) == ("es", True, True)
    with pytest.raises(ReachError, match="no subtitles"):
        youtube._pick_subtitle_track({"subtitles": {}, "automatic_captions": {}}, _ES)


def test_subtitle_downloads_exactly_one_track_from_the_fetched_info(monkeypatch):
    info = {"id": "jTwm4xs5y4c", "title": "4 Rust tips", "language": "en",
            "subtitles": {}, "automatic_captions": {"en-orig": [{}], "es": [{}]}}
    calls = []

    def fake_run(args, timeout, cwd=None):
        calls.append(args)
        if "--dump-json" in args:
            return json.dumps(info)
        with open(os.path.join(cwd, "jTwm4xs5y4c.en-orig.vtt"), "w", encoding="utf-8") as fh:
            fh.write("WEBVTT\n\n00:00:00.000 --> 00:00:02.000\nbuild a honeycomb\n")
        return ""

    monkeypatch.setattr(youtube, "_run_ytdlp", fake_run)
    items = YouTubeChannel()._ytdlp_subtitle(target="jTwm4xs5y4c", lang=",".join(_ES), timeout=30)
    download = calls[1]
    assert len(calls) == 2 and "--load-info-json" in download
    assert download[download.index("--sub-langs") + 1] == "en-orig" and "--write-auto-subs" in download
    assert items[0]["title"] == "4 Rust tips" and "honeycomb" in items[0]["text"]
    assert items[0]["raw"]["lang"] == "en-orig" and items[0]["raw"]["translated"] is False
