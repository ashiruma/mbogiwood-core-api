# films/tasks.py

import subprocess
from pathlib import Path
from celery import shared_task
from django.conf import settings
from .models import Film

@shared_task
def convert_film_to_hls(film_id):
    try:
        film = Film.objects.get(id=film_id)
        film.processing_status = Film.ProcessingStatus.PROCESSING
        film.save()

        # Input and output paths
        source_path = film.video_file.path
        output_dir = Path(settings.MEDIA_ROOT) / 'hls' / str(film.id)
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / "manifest.m3u8"

        # FFmpeg command to convert the video
        command = [
            'ffmpeg',
            '-i', str(source_path),
            '-profile:v', 'baseline',  # for wide compatibility
            '-level', '3.0',
            '-start_number', '0',
            '-hls_time', '10',  # 10-second segments
            '-hls_list_size', '0',  # keep all segments in the playlist
            '-f', 'hls',
            str(manifest_path),
        ]

        subprocess.run(command, check=True)

        # Save the path to the manifest file
        film.hls_manifest_path = str(manifest_path.relative_to(settings.MEDIA_ROOT))
        film.processing_status = Film.ProcessingStatus.SUCCESS
        film.save()

    except Film.DoesNotExist:
        # Handle case where film is not found
        pass
    except subprocess.CalledProcessError as e:
        # Handle ffmpeg conversion errors
        film.processing_status = Film.ProcessingStatus.FAILED
        film.save()
        # You might want to log the error `e` here
    except Exception as e:
        # Handle other unexpected errors
        film.processing_status = Film.ProcessingStatus.FAILED
        film.save()