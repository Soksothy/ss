# API interaction module for YouTube Shorts Harvester
import logging
from typing import List, Dict
from urllib.parse import urlparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import isodate


def build_youtube_client(api_key: str):
    """Build the YouTube API client."""
    return build("youtube", "v3", developerKey=api_key, cache_discovery=False)


def resolve_channel_id(youtube, channel_url: str) -> str:
    """Resolve various YouTube channel URL formats to a channel ID."""
    parsed = urlparse(channel_url)
    path_parts = [p for p in parsed.path.split("/") if p]
    identifier = None
    if not path_parts:
        raise ValueError("Invalid channel URL")

    if path_parts[0] == "channel" and len(path_parts) > 1:
        return path_parts[1]

    if path_parts[0].startswith("@"):  # handle
        identifier = path_parts[0][1:]
    elif path_parts[0] in {"c", "user"} and len(path_parts) > 1:
        identifier = path_parts[1]
    else:
        identifier = path_parts[0]

    request = youtube.search().list(q=identifier, type="channel", maxResults=1)
    response = request.execute()
    items = response.get("items", [])
    if not items:
        raise ValueError("Channel not found")
    return items[0]["snippet"]["channelId"]


def fetch_shorts_metadata(youtube, channel_id: str, max_results: int, logger=logging.getLogger(__name__)) -> List[Dict]:
    """Fetch latest shorts (<=60s) metadata from a channel."""
    results = []
    next_token = None
    fetched = 0
    while fetched < max_results:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            order="date",
            maxResults=min(50, max_results - fetched),
            pageToken=next_token,
        )
        response = request.execute()
        ids = [item["id"].get("videoId") for item in response.get("items", []) if item["id"].get("videoId")]
        if not ids:
            break
        vids_request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(ids),
        )
        vids_response = vids_request.execute()
        for item in vids_response.get("items", []):
            duration = isodate.parse_duration(item["contentDetails"]["duration"]).total_seconds()
            if duration <= 60:
                results.append({
                    "video_id": item["id"],
                    "title": item["snippet"].get("title", ""),
                    "description": item["snippet"].get("description", ""),
                    "published_at": item["snippet"].get("publishedAt", ""),
                    "view_count": item.get("statistics", {}).get("viewCount", ""),
                    "duration_seconds": int(duration),
                    "like_count": item.get("statistics", {}).get("likeCount", ""),
                })
        fetched = len(results)
        next_token = response.get("nextPageToken")
        if not next_token:
            break
    return results[:max_results]


def fetch_transcript(video_id: str) -> str:
    """Fetch transcript text for a video ID."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except (TranscriptsDisabled, NoTranscriptFound, HttpError):
        return "Unavailable"

