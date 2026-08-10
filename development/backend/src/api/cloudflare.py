from pathlib import Path
import requests
import re
from faster_whisper import WhisperModel
import json

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BACKEND_DIR/"data"
DATA_DIR.mkdir(exist_ok=True)
TEST_TRANSCRIPT_FILE = DATA_DIR/"test_transcript.json"
TRANSCRIPT_URLS_FILE = DATA_DIR/"transcript_urls.json"
WORKER_URL = "https://cloudflare-worker.kangcohen.workers.dev"

# initialize whisper model for audio transcription
model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)

def transcribe(audio_path):
    """ uses whisper model to turn audio to text when no transcripts are available """
    segments, _ = model.transcribe(audio_path)
    return " ".join(seg.text for seg in segments)

def parse_vtt_text(vtt):
    """ function to parse the transcript files returned by yt-dlp """
    text = []
    for line in vtt.splitlines():
        line = line.strip()

        if line.isdigit():
            continue

        if not line or "-->" in line or "WEBVTT" in line:
            continue

        line = re.sub(r"<[^>]+>", "", line)
        text.append(line)

    return " ".join(text)

def download_urls(url_objs, logger):
    transcripts = {}
    for id, value in url_objs.items():
        result = None
        title = value["title"]
        payload = {
            "url": value["url"],
            "headers": value.get("headers", {}),
        }
        src_type = value["type"]
        response = requests.post(WORKER_URL,json=payload,timeout=60,)
        if response.status_code != 200:
            print("Response:", response.text[:500])

        response.raise_for_status()

        if src_type == "text":
            result = parse_vtt_text(response.text)
            logger.info(f"{id}: Success, yt_dlp downloaded text transcript")
        else:
            ext = value.get("ext", "webm")
            audio_path = DATA_DIR / f"{id}.{ext}"

            try:
                with open(audio_path, "wb") as f:
                    f.write(response.content)

                result = transcribe(audio_path)
            except Exception as e:
                logger.error(
                    f"{id}: Audio transcription failed: {e}"
                )
                continue
            finally:
                if audio_path.exists():
                    audio_path.unlink()
            logger.info(f"{id}: Success, yt_dlp downloaded video audio and was transcibed")

        transcripts[id] = {
            "title": title,
            "source": src_type,
            "transcript": result
        }
        with open(TEST_TRANSCRIPT_FILE, 'w') as f:
            json.dump(transcripts,f, indent=4)
