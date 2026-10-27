# -*- coding: utf-8 -*-
"""Short videos from TikTok and Instagram Reels through yt-dlp, without the browser or a login.

Public posts only. Instagram often answers yt-dlp with "login required" or a rate
limit; this channel never logs in, so those cases end as an error for the user.
"""

import re
from urllib.parse import urlsplit

from agent_reach.runtime.result import BAD_INPUT, ReachError
from agent_reach.utils.url import host_matches

from .base import Action, Channel, Param
from .youtube import whisper_transcribe, ytdlp_info, ytdlp_subtitle

_TIKTOK = ("tiktok.com",)
_INSTAGRAM = ("instagram.com",)
_INSTAGRAM_VIDEO_PATH = re.compile(r"^/(?:[^/]+/)?(?:reels?|p|tv)/[A-Za-z0-9_-]+/?$")


def _video_url(target: str) -> str:
    t = str(target).strip()
    candidate = t if "://" in t else f"https://{t}"
    if host_matches(candidate, *_TIKTOK):
        return candidate
    if host_matches(candidate, *_INSTAGRAM) and _INSTAGRAM_VIDEO_PATH.match(urlsplit(candidate).path):
        return candidate
    raise ReachError(BAD_INPUT, "target must be a TikTok video link or an Instagram reel/post link")


class VideoChannel(Channel):
    name = "video"
    description = "Vídeos cortos públicos de TikTok e Instagram Reels"

    level = "default"
    #: transcribe re-encodes and chunks audio
    prereqs = ("ffmpeg",)
    actions = (
        Action(
            "read",
            "Caption, author, date and stats of a TikTok video or Instagram reel",
            (Param("target", "TikTok or Instagram reel link"),),
            (("yt-dlp", "_ytdlp_read"),),
            live_test={"target": "https://www.tiktok.com/@scout2015/video/6718335390845095173"},
        ),
        Action(
            "subtitle",
            "Subtitle text when the video has captions (one track, never machine-translated first)",
            (
                Param("target", "TikTok or Instagram reel link"),
                Param("lang", "preferred languages for human subtitles, comma separated; otherwise the video's own language",
                      required=False, default="es,es-ES,es-419,en"),
            ),
            (("yt-dlp", "_ytdlp_subtitle"),),
        ),
        Action(
            "transcribe",
            "Speech-to-text of the video's audio (uses Groq/OpenAI Whisper quota)",
            (Param("target", "TikTok or Instagram reel link"),),
            (("whisper", "_whisper_transcribe"),),
            timeout=600,
        ),
    )

    def can_handle(self, url: str) -> bool:
        try:
            _video_url(url)
        except ReachError:
            return False
        return True

    def validate_params(self, action, params):
        params["target"] = _video_url(params["target"])

    # ── unified entry backends ──

    def _ytdlp_read(self, *, target: str, timeout: float) -> list:
        return ytdlp_info(_video_url(target), timeout)

    def _ytdlp_subtitle(self, *, target: str, lang: str, timeout: float) -> list:
        return ytdlp_subtitle(_video_url(target), lang, timeout)

    def _whisper_transcribe(self, *, target: str, timeout: float) -> list:
        return whisper_transcribe(_video_url(target))
