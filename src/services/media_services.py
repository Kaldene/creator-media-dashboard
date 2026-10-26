import os
import yt_dlp
import logging
from pathlib import Path
from functools import wraps
from urllib.parse import urlparse
from yt_dlp.networking.impersonate import ImpersonateTarget
from sqlalchemy.orm import Session
from src.api.media.models import VideoItem, AudioItem

def validate_url(func):
    @wraps(func)
    def wrapper(self, url: str, *args, **kwargs):
        if not url or not isinstance(url, str):
            raise ValueError("URL должен быть непустой строкой")

        parsed = urlparse(url)
        if not all([parsed.scheme in ['http', 'https'], parsed.netloc]):
            raise ValueError(f"Некорректный формат URL: {url}")

        return func(self, url, *args, **kwargs)

    return wrapper


class MediaService:
    def __init__(self, download_path: str = "download"):
        current_file_path = Path(__file__).parent.resolve()
        project_root_path = current_file_path.parent

        # Определяем базовую папку и подпапки
        self.base_download_path = project_root_path / download_path
        self.video_path = self.base_download_path / "video"
        self.audio_path = self.base_download_path / "audio"

        # Создаем директории
        os.makedirs(self.video_path, exist_ok=True)
        os.makedirs(self.audio_path, exist_ok=True)

        self.base_opts = {
            "geo_bypass": True,
            "quiet": True,
            "no_progress": True,
            "noplaylist": True,
            "impersonate": ImpersonateTarget(client="firefox"),
        }

    @validate_url
    def download_media_metadata(self, url: str) -> dict:
        opts = self.base_opts.copy()
        opts["skip_download"] = True
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "status": 200,
                    "title": info.get("title"),
                    "upload_date": info.get("upload_date"),
                    "view_count": info.get("view_count"),
                    "like_count": info.get("like_count"),
                    "comment_count": info.get("comment_count"),
                    "duration": info.get("duration"),
                    "description": info.get("description")
                }
        except Exception as e:
            logging.error(f"Metadata error: {e}")
            return {"message": "не получилось собрать метаданные", "status": 404}

    @validate_url
    def download_media(self, url: str, resolution: int = 1080) -> dict:
        opts = self.base_opts.copy()
        opts["skip_download"] = False
        opts["format"] = f"bestvideo[height<={resolution}]+bestaudio/best"
        opts["merge_output_format"] = "mp4"
        opts["quiet"] = False
        opts["no_progress"] = False

        opts["outtmpl"] = f"{self.video_path}/%(id)s_%(title)s.%(ext)s"

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return {
                    "status": 200,
                    "file_path": ydl.prepare_filename(info),
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "view_count": info.get("view_count")
                }
        except Exception as e:
            logging.error(f"Download media error: {e}")
            return {"message": "не получилось скачать видео", "status": 404}

    @validate_url
    def download_audio(self, url: str) -> dict:
        opts = self.base_opts.copy()
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }]
        opts["quiet"] = False
        opts["no_progress"] = False

        # Направляем аудио в папку /download/audio
        opts["outtmpl"] = f"{self.audio_path}/%(id)s_%(title)s.%(ext)s"

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                original_file = ydl.prepare_filename(info)
                base_name, _ = os.path.splitext(original_file)
                final_audio_path = f"{base_name}.m4a"

                return {
                    "status": 200,
                    "file_path": final_audio_path,
                    "title": info.get("title"),
                    "duration": info.get("duration"),
                    "view_count": info.get("view_count")
                }
        except Exception as e:
            logging.error(f"Download audio error: {e}")
            return {"message": "не получилось скачать аудио", "status": 404}

    def delete_media(self, file_path: str) -> None:
        try:
            target_path = Path(file_path).resolve()
            allowed_dir = self.base_download_path.resolve()


            if not target_path.is_relative_to(allowed_dir):
                logging.warning(f"Попытка удаления файла вне папки загрузок: {target_path}")
                return

            if target_path.suffix.lower() not in [".mp4", ".m4a"]:
                logging.warning(f"Попытка удалить файл с запрещенным расширением: {target_path}")
                return

            if target_path.exists() and target_path.is_file():
                target_path.unlink()
        except Exception as e:
            logging.error(f"Не удалось удалить файл {file_path}: {e}")


from src.api.media.models import VideoItem, AudioItem


class MediaRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_record(self, user_id: int, url: str, media_type: str, data: dict, file_path: str = None):
        # Выбираем нужную модель
        ModelClass = VideoItem if media_type == "video" else AudioItem

        new_media = ModelClass(
            user_id=user_id,
            url=url,
            title=data.get("title"),
            file_path=file_path or data.get("file_path"),
            duration=data.get("duration"),
            view_count=data.get("view_count")
        )

        self.db.add(new_media)
        self.db.commit()
        self.db.refresh(new_media)

        return new_media

ser = MediaService()
url = "https://youtu.be/AF4a5M-VJXo?si=nE8PJNWX0ulO1aEH"
delete_path = r'C:\Users\Sonder\Desktop\aBOBA\src\download\audio\AF4a5M-VJXo_Cyberpunk： Edgerunners 2 OST - Talia Theme [Out of Bounds].m4a'
# ser.download_audio(url)
# ser.download_media(url)
ser.delete_media(delete_path)