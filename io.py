# IO utilities for YouTube Shorts Harvester
import csv
import os
from typing import List, Dict


def save_rows_to_csv(rows: List[Dict], folder: str, filename: str = "shorts_data.csv") -> str:
    """Save a list of dicts to CSV in the specified folder."""
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    fieldnames = [
        "video_id",
        "title",
        "description",
        "published_at",
        "view_count",
        "duration_seconds",
        "like_count",
        "transcript_text",
    ]
    with open(path, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return path
