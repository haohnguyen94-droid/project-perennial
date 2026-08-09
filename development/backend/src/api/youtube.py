import os
import json
import googleapiclient.discovery
import yt_dlp
from faster_whisper import WhisperModel
import glob
import time
import random
import re
from dotenv import load_dotenv
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from yt_dlp.utils import DownloadError
from src.utils.youtube_logger import create_logger
from collections import deque
from pathlib import Path
import argparse

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BACKEND_DIR/"data"
DATA_DIR.mkdir(exist_ok=True)
METADATA_FILE = DATA_DIR/"metadata.json"
TRANSCRIPT_URLS_FILE = DATA_DIR/"transcript_urls.json"
STATUS_FILE = DATA_DIR/"status.json"

### compute the beginning of last month for video timeframes
now = datetime.now(timezone.utc)
published_after = (
    now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=1)
).strftime("%Y-%m-%dT%H:%M:%SZ")
###

load_dotenv()

# main options for YT-DLP calls attached to other options in get_transcripts
YDL_OPTS = {
    "quiet": True,
    "retries": 2,
    "fragment_retries": 2,
    "sleep_interval_requests": 2,
    "skip_download": True,
    "subtitlesformat": "vtt",
    "quiet": True,  
    "no_warnings": True,
    "verbose": False
    # "cookiesfrombrowser": ("chrome",), (use this line instead of the one above if you are on chrome)
}


def get_video_ids_and_metadata(keyword, logger):
    """ given a keyword return list of objects from Youtube API that are related to the keyword """
    page_token = None
    results = []
    videoIds = []
    logger.info("started metadata gathering")
    youtube = googleapiclient.discovery.build(
        "youtube",
        "v3",
        developerKey=os.getenv("YOUTUBE_API_KEY")
    )
    
    while True:
        request = youtube.search().list(
            part="snippet",
            maxResults=50,
            order="date",
            publishedAfter=published_after,
            q=keyword,
            type="video",
            fields="nextPageToken, items(id/videoId)",
            pageToken=page_token
        )
        response = request.execute()
        results.extend(response.get("items",[]))

        page_token = response.get("nextPageToken")

        if not page_token:
            break

    for item in results:
        videoIds.append(item["id"]["videoId"])
        
    # get metadata from video IDs above
    metadata = load_json(METADATA_FILE, {}) # dictionary with previously fetched metadata
        
    details: dict[str, dict] = {}
    for i in range(0, len(videoIds), 50):
        batchIds = videoIds[i:i+50]
        request = youtube.videos().list(
            part="statistics,snippet,contentDetails",
            fields="items(id,snippet/title,snippet/channelTitle,snippet/publishedAt,snippet/tags,statistics/viewCount,statistics/likeCount,contentDetails/duration)",
            id = ",".join(batchIds)
        )
        response = request.execute()

        for item in response.get("items",[]):
            details[item['id']] = item

    for videoId in videoIds:
        if videoId in metadata:
            continue

        item = details.get(videoId)
        # if video is removed between execution
        if item is None:
            continue

        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        contentDetails = item.get("contentDetails", {})

        metadata[videoId]={
            "title": snippet.get("title"),
            "channel": snippet.get("channelTitle"),
            "publishedDate": snippet.get("publishedAt"),
            "tags": snippet.get("tags",[]),
            "viewCount": int(statistics.get("viewCount",0)),
            "likeCount": int(statistics.get("likeCount",0)),
            "duration": contentDetails.get("duration", "PT0S")
        }
        logger.info(f"{videoId}: metadata success")

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent = 4)

    return videoIds

def parse_vtt(path):
    """ function to parse the transcript files returned by yt-dlp """
    text = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.isdigit():
                continue
            line = line.strip()
            if not line or "-->" in line or "WEBVTT" in line:
                continue
            line = re.sub(r"<[^>]+>", "", line)
            text.append(line)
    return " ".join(text)

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

def load_json(path, default):
    """helper function to load json files"""

    #if filepath is bad return default
    if not os.path.exists(path):
        return default

    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()

        #if json is empty return default
        if not content:
            return default
        
        return json.loads(content)
    
def get_transcripts(videoIds, logger):
    """ 
    function that handles main logic of fetching transcript 
    yt_dlp will get metadata again for transcripts
    yt_dlp API call is more expensive than bulk batching 50 youtube API calls
    therefore do any filtering of videos before calling this function
    this function should only be called on videoIDs we care about to save bandwidth
    """
    data = load_json(METADATA_FILE, {})
    transcript_urls = load_json(TRANSCRIPT_URLS_FILE, {})
    os.makedirs("data", exist_ok=True)

    ids = deque(videoIds[:20])
    status = check_status(videoIds)
    count = 0
            
    while ids:
        id = ids.popleft()
        print(f"\rGetting urls: {count}/{len(videoIds)}", end="", flush=True)

        current_status = status[id]
        if current_status == "done" or int(current_status) >= 5:
            logger.info(f"{id}: skipping metadata, done or tries exceeded")
            count += 1
            continue
        
        current_status = int(current_status) + 1
        status[id] = str(current_status)
        update_status(status)

        url = f"https://www.youtube.com/watch?v={id}"
        current_status = status[id]


        try:
            time.sleep(random.uniform(2+(4*int(current_status)), 5+(4*int(current_status))))
            with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
                info = ydl.extract_info(url, download=False)
        except DownloadError as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                logger.warning(f"{id}: Failed, Rate limited by API, retrying later")
                ids.append(id)
                continue
            else:
                logger.error(f"{id}: Failed, download error")
                continue
        except Exception as e:
            logger.error(f"{id}: Failed, unknown error: {e}")
            continue

        manual = info.get("subtitles", {})
        english_manual = next(
            (lang for lang in manual if lang.lower().startswith("en")),
            None
        )
        automatic = info.get("automatic_captions", {})
        english_automatic = next(
            (lang for lang in automatic if lang.lower().startswith("en")),
            None
        )

        src_type = None
        lang = None
        if english_manual:
            src_type = "text"
            lang = english_manual
        elif english_automatic:
            src_type = "text"
            lang = english_automatic
        else:
            src_type = "audio"


        title = data.get(id,{}).get("title", "")
            
        if src_type == "text":
            english_tracks = None

            english_tracks = info.get("subtitles", {}).get(lang, [])
            if not english_tracks:
                english_tracks = info.get("automatic_captions",{}).get(lang, [])

            track = next((t for t in english_tracks if t.get("ext") == "vtt"), None)

            if track:
                transcript_urls[id] = {
                    "url": track["url"],
                    "headers": track.get("http_headers", {}),
                    "title": title,
                    "type": "text",
                }
                logger.info(f"{id}: Success, yt_dlp returned transcript url")
            else:
                logger.error(f"{id}: Failed, to get caption url")
                continue
        else:
            formats = info.get("formats", [])
            if not formats:
                logger.error(f"{id}: Failed, no formats found")
                continue

            audio_formats = [
                fmt
                for fmt in formats
                if fmt.get("vcodec") == "none"
                and fmt.get("acodec") != "none"
            ]
            if not audio_formats:
                logger.error(f"{id}: Failed, no audio formats found")
                continue
            # pick audio format with the highest bitrate
            audio = max(audio_formats,key=lambda fmt: fmt.get("abr") or 0,)

            transcript_urls[id] = {
                "url": audio["url"],
                "headers":audio.get("http_headers",{}),
                "title": title,
                "type": "audio"
            }
            logger.info(f"{id}: Success, yt_dlp returned audio url")


        status[id] = "done"
        logger.info(f"{id}: Done")
        count += 1

        update_status(status)
        with open(TRANSCRIPT_URLS_FILE, "w", encoding="utf-8") as f:
            json.dump(transcript_urls, f, indent = 4, ensure_ascii=False)

def check_status(video_ids):
    """ returns status state for each video ID to prevent unnecessary work """

    #TODO: this function works together with update_status and is currently being saved and fetched via JSON
    #      in the future probably migrate to a SQL or some other database

    results = {}
    cache = load_json(STATUS_FILE, {})
        
    for id in video_ids:
        results[id] = cache.get(id, "0")

    return results

def update_status(states):
    """ stores status state for each video ID to prevent unnecessary work """

    #TODO: this function works together with check_status and is currently being saved and fetched via JSON
    #      in the future probably migrate to a SQL or some other database
    status = load_json(STATUS_FILE, {})
    
    for state in states.keys():
        if state not in status.keys() or status[state] != states[state]:
            status[state] = states[state]
    
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent = 4)

def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube transcripts given keyword."
    )
    parser.add_argument(
        "keyword",
        help="Keyword to search for"
    )
    args = parser.parse_args()
    keyword = f'{args.keyword}'
    print(f"Searching for: {keyword}")
  
    logger = create_logger(keyword+".log")
    videoIds = get_video_ids_and_metadata(f'"{keyword}"', logger)
    get_transcripts(videoIds, logger)

    return

if __name__ == "__main__":
    main()