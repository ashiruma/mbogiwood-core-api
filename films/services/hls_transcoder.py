import os
import subprocess
from pathlib import Path


FFMPEG_BIN = os.environ.get("FFMPEG_BIN", "ffmpeg")


def transcode_to_hls(source_path: str, output_dir: str, playlist_name: str = "index.m3u8") -> str:
"""
Convert MP4 (or other) to HLS.
Returns path to generated playlist.
"""
Path(output_dir).mkdir(parents=True, exist_ok=True)
playlist_path = os.path.join(output_dir, playlist_name)


# Simple 720p ladder (tweak as needed)
cmd = [
FFMPEG_BIN,
"-y", "-i", source_path,
"-profile:v", "main", "-level", "3.1",
"-start_number", "0", "-hls_time", "6", "-hls_list_size", "0",
"-f", "hls", playlist_path,
]
subprocess.check_call(cmd)
return playlist_path