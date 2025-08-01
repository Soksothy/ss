# Entry point for YouTube Shorts Harvester
import sys
import threading
import datetime
import logging

from PyQt5 import QtWidgets

from ui import MainWindow
from api import build_youtube_client, resolve_channel_id, fetch_shorts_metadata, fetch_transcript
from io import save_rows_to_csv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


class Worker(threading.Thread):
    def __init__(self, window: MainWindow, api_key: str, channel_url: str, max_shorts: int, folder: str):
        super().__init__()
        self.window = window
        self.api_key = api_key
        self.channel_url = channel_url
        self.max_shorts = max_shorts
        self.folder = folder
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        try:
            youtube = build_youtube_client(self.api_key)
            self.window.log("Resolving channel ID...")
            channel_id = resolve_channel_id(youtube, self.channel_url)
            self.window.log(f"Channel ID: {channel_id}")
            shorts = fetch_shorts_metadata(youtube, channel_id, self.max_shorts)
            rows = []
            for idx, data in enumerate(shorts, 1):
                if self._stop_event.is_set():
                    break
                self.window.log(f"Fetching transcript {idx}/{len(shorts)}: {data['title']}")
                transcript = fetch_transcript(data['video_id'])
                data['transcript_text'] = transcript
                rows.append(data)
            if rows:
                path = save_rows_to_csv(rows, self.folder)
                self.window.log(f"Saved to {path}")
            self.window.log("Done")
        except Exception as e:
            self.window.log(f"Error: {e}")


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    worker = None

    def start(api_key, channel_url, max_shorts, folder):
        nonlocal worker
        if max_shorts > 200:
            QtWidgets.QMessageBox.warning(window, "Warning", "Fetching more than 200 shorts may exceed your API quota.")
        worker = Worker(window, api_key, channel_url, max_shorts, folder)
        worker.start()

    def cancel():
        if worker:
            worker.stop()
            window.log("Cancelling...")

    window.start_clicked.connect(start)
    window.cancel_clicked.connect(cancel)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
