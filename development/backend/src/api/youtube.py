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

### compute the beginning of last month for video timeframes
now = datetime.now(timezone.utc)
published_after = (
    now.replace(day=1, hour=0, minute=0, second=0, microsecond=0) - relativedelta(months=1)
).strftime("%Y-%m-%dT%H:%M:%SZ")
###

load_dotenv()

# main options for YT-DLP calls attached to other options in get_transcripts
COMMON_YDL_OPTS = {
    "quiet": True,
    "retries": 2,
    "fragment_retries": 2,
    "sleep_interval_requests": 2,
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
    metadata = load_json("metadata.json", {}) # dictionary with previously fetched metadata
        
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

    with open("metadata.json", "w") as f:
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

    with open(path, "r") as f:
        content = f.read().strip()

        #if jsono is empty return default
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
    data = load_json("metadata.json", {})
    transcripts = load_json("transcripts.json", {})
    os.makedirs("data", exist_ok=True)

    ids, titles = [], []

    for id in videoIds:
        ids.append(id)
        titles.append(data[id]["title"])

    status = check_status(ids)

    # array slicing here for testing purposes, remove the slice operator during launch
    for i in range(len(ids)):
        id, title = ids[i], titles[i]
        current_status = status[id]
        if current_status == "done" or int(current_status) >= 3:
            logger.info(f"{id}: skipping, done or tries exceeded")
            continue
 
        url = f"https://www.youtube.com/watch?v={id}"
        result = None

        current_status = int(current_status)
        current_status += 1
        logger.info(f"{id}: processing, {str(current_status)}/3")
        print(f"Processing ID:{id}, {str(current_status)}/3")
        
        try:
            with yt_dlp.YoutubeDL(COMMON_YDL_OPTS) as ydl:
                time.sleep(random.uniform(3, 10))
                info = ydl.extract_info(url, download=False)
            logger.info(f"{id}: yt_dlp metadata success")
        except Exception as e:
            print(f"{id}: metadata failed: {e}")
            logger.error(f"{id}: yt_dlp metadata failed")
            status[id] = str(current_status)
            continue
        
        opts = None
        src_type = None

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

        # search parameters for yt_dlp to try and get any transcripts from youtube API
        if english_manual:
            opts = {
                **COMMON_YDL_OPTS,
                "skip_download": True,
                "subtitlesformat": "vtt",
                "writesubtitles": True,
                "writeautomaticsub": False,
                "subtitleslangs": [english_manual],
                "outtmpl": f"data/{id}.%(ext)s",
                "quiet": True,
            }
            src_type = "text"
        elif english_automatic:
            opts = {
                **COMMON_YDL_OPTS,
                "skip_download": True,
                "subtitlesformat": "vtt",
                "writesubtitles": False,
                "writeautomaticsub": True,
                "subtitleslangs": [english_automatic],
                "outtmpl": f"data/{id}.%(ext)s",
                "quiet": True,
            }
            src_type = "text"
        else:
            opts = {
                **COMMON_YDL_OPTS,
                "format": "bestaudio/best",
                "outtmpl": "data/%(id)s.%(ext)s",
                "quiet": True,
                "sleep_interval": 10,
                "max_sleep_interval": 30,
            }
            src_type = "audio"
        
        try:
            time.sleep(random.uniform(5, 15))
            ydl = yt_dlp.YoutubeDL(opts)
            ydl.download([url])
        except DownloadError as e:
            # if call is blocked due to being rate limited, then don't count this try
            if "429" in str(e) or "Too Many Requests" in str(e):
                print(f"{id}: Rate limited by Youtube API, retrying later")
                logger.warning(f"{id}: Failed, Rate limited by API, retrying later")
                continue
            else:
                print(f"{id}: download failed: {e}")
                status[id] = str(current_status)
                logger.error(f"{id}: Failed, download error")
                continue
        except Exception as e:
            print(f"{id}: unknown exception: {e}")
            status[id] = str(current_status)
            logger.error(f"{id}: Failed, unknown error: {e}")
            continue
            
        if src_type == "text":
            matches = sorted(glob.glob(f"data/{id}*.vtt"))
            if not matches:
                print(f"{id}: no matches found")
                status[id] = str(current_status)
                continue
            path = matches[0]
            result = parse_vtt(path) if path else None
            logger.info(f"{id}: Success, yt_dlp downloaded text transcript")
        else:
            matches = sorted(glob.glob(f"data/{id}.*"))
            matches = [
                path for path in matches
                if path.endswith((".mp3", ".m4a", ".webm", ".opus", ".wav"))
            ]
            if not matches:
                print(f"{id}: no matches found")
                status[id] = str(current_status)
                continue
            path = matches[0]
            result = transcribe(path) if path else None
            logger.info(f"{id}: Success, yt_dlp downloaded video audio and was transcibed")

        transcripts[id] = {
            "title": title,
            "source": src_type,
            "transcript": result
        }
        status[id] = "done"
        os.remove(path)
        logger.info(f"{id}: Done")

    update_status(status)
    with open("transcripts.json", "w") as f:
        json.dump(transcripts, f, indent = 4)

def check_status(video_ids):
    """ returns status state for each video ID to prevent unnecessary work """

    #TODO: this function works together with update_status and is currently being saved and fetched via JSON
    #      in the future probably migrate to a SQL or some other database

    results = {}
    cache = load_json("cache.json", {})
        
    for id in video_ids:
        results[id] = cache.get(id, "0")

    return results

def update_status(states):
    """ stores status state for each video ID to prevent unnecessary work """

    #TODO: this function works together with check_status and is currently being saved and fetched via JSON
    #      in the future probably migrate to a SQL or some other database
    status = load_json("status.json", {})
    
    for state in states.keys():
        if state not in status.keys() or status[state] != states[state]:
            status[state] = states[state]
    
    with open("status.json", "w") as f:
        json.dump(status, f, indent = 4)

def main():
    keyword = "Palantir"
    logger = create_logger(keyword+".log")
    videoIds = get_video_ids_and_metadata(keyword, logger)
    get_transcripts(videoIds, logger)

    return

if __name__ == "__main__":
    main()