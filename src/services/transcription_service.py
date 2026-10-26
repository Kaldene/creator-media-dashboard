import logging
from pathlib import Path
import traceback

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)


class SrtService:

    @staticmethod
    def format_time(seconds: float) -> str:
        # ИСПРАВЛЕНО: Правильное умножение
        ms = round(seconds * 1000)
        hours, ms = divmod(ms, 3600000)
        minutes, ms = divmod(ms, 60000)
        secs, ms = divmod(ms, 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"

    def format_srt_block(self, number: int, text: str, start_time: float, end_time: float) -> str:
        start = self.format_time(start_time)
        end = self.format_time(end_time)
        return f"{number}\n{start} --> {end}\n{text.strip()}\n"

    def write(self, segments, srt_path: str | Path) -> None:
        try:
            with open(srt_path, "w", encoding="utf-8") as f:
                for number, s in enumerate(segments, start=1):
                    block = self.format_srt_block(number, s.text, s.start, s.end)
                    f.write(block + "\n")
        except Exception as e:
            raise ValueError("Не получилось записать субтитры") from e

    def is_garbage(self, segment, previous_text: str | None) -> bool:
        text = segment.text.strip()
        return not text or text == previous_text

    def clean_segments(self, segments) -> list:
        result = []
        previous_text = None
        for s in segments:
            if self.is_garbage(s, previous_text):
                print(f"УДАЛЕНО [{s.start:.1f}-{s.end:.1f}]: {s.text!r}")
                continue
            result.append(s)
            previous_text = s.text.strip()
        return result


class TranscriptionService:
    def __init__(self, model_size: str = "small"):
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        self.srt = SrtService()

    def transcribe_audio(self, audio_path: str, language: str | None = None) -> dict:
        try:
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=5,
                language=language,
                condition_on_previous_text=False,
            )

            segments = list(segments)
            full_text = "".join(s.text for s in segments).strip()

            return {
                "status": 200,
                "language": info.language,
                "text": full_text,
                "segments": [
                    {"start": s.start, "end": s.end, "text": s.text.strip()}
                    for s in segments
                ],
            }

        except Exception as e:
            logger.exception(f"Ошибка распознавания: {e}")
            return {"status": 500, "message": "Не удалось перевести аудио в текст"}

    def generate_subtitles(self, audio_path: str, language: str | None = None) -> Path:
        # ДОБАВЛЕН БЛОК TRY-EXCEPT для отлова реальных ошибок (например, нехватка FFmpeg)
        try:
            segments, info = self.model.transcribe(
                audio_path,
                language=language,
                condition_on_previous_text=False,
            )
            segments = list(segments)

            print(f"Язык: {info.language} ({info.language_probability:.2f})")

            segments = self.srt.clean_segments(segments)
            srt_path = Path(audio_path).with_suffix(".srt")
            self.srt.write(segments, srt_path)

            return srt_path
        except Exception as e:
            # Выводим полную красную ошибку в консоль сервера
            print("--- КРИТИЧЕСКАЯ ОШИБКА WHISPER ---")
            traceback.print_exc()
            raise ValueError(f"Ошибка Whisper: {str(e)}")