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

load_dotenv()

# main options for YT-DLP calls attached to other options in get_transcripts
COMMON_YDL_OPTS = {
    "quiet": True,
    "retries": 2,
    "fragment_retries": 2,
    "sleep_interval_requests": 2,
}

def get_videos(keyword):
    """ given a keyword return list of objects from Youtube API that are related to the keyword """
    page_token = None
    results = []
    
    youtube = googleapiclient.discovery.build(
        "youtube",
        "v3",
        developerKey=os.getenv("YOUTUBE_API_KEY")
    )
    
    while True:
        request = youtube.search().list(
            part="snippet",
            maxResults=50,
            q=keyword,
            type="video",
            fields="nextPageToken, items(id/videoId,snippet/title,snippet/channelTitle)",
            pageToken=page_token
        )
        response = request.execute()
        results.extend(response["items"])

        page_token = response.get("nextPageToken")

        if not page_token:
            break

    with open("data.json", "w") as f:
        json.dump(results, f, indent = 4)

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

model = WhisperModel("tiny")
def transcribe(audio_path):
    """ uses whisper model to turn audio to text when no transcripts are available """
    segments, _ = model.transcribe(audio_path)
    return " ".join(seg.text for seg in segments)

def load_json(path, default):
    if not os.path.exists(path):
        return default

    with open(path, "r") as f:
        return json.load(f)
    
def get_transcripts():
    """ function that handles main logic of determining transcript source """
    data = load_json("data.json", [])
    transcripts = load_json("transcripts.json", {})
    os.makedirs("data", exist_ok=True)

    ids = [
        video["id"]["videoId"]
        for video in data
        if video.get("id", {}).get("videoId")
    ]
    titles = [
        video["snippet"]["title"]
        for video in data
        if video.get("id", {}).get("videoId")
    ]

    cache = check_cache(ids)

    for i in range(len(ids[:5])):
        id, title = ids[i], titles[i]
        status = cache[id]
        if status == "done" or int(status) >= 3:
            continue
 
        url = f"https://www.youtube.com/watch?v={id}"
        result = None

        status = int(status)
        status += 1
        print(f"Processing ID:{id}, {str(status)}/3")
        
        try:
            with yt_dlp.YoutubeDL(COMMON_YDL_OPTS) as ydl:
                time.sleep(random.uniform(3, 10))
                info = ydl.extract_info(url, download=False)
        except Exception as e:
            print(f"{id}: metadata failed: {e}")
            cache[id] = str(status)
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
        except Exception as e:
            print(f"{id}: download failed: {e}")
            cache[id] = str(status)
            continue
        
        if src_type == "text":
            matches = sorted(glob.glob(f"data/{id}*.vtt"))
            if not matches:
                print(f"{id}: no matches found")
                cache[id] = str(status)
                continue
            path = matches[0]
            result = parse_vtt(path) if path else None
        else:
            matches = sorted(glob.glob(f"data/{id}.*"))
            matches = [
                path for path in matches
                if path.endswith((".mp3", ".m4a", ".webm", ".opus", ".wav"))
            ]
            if not matches:
                print(f"{id}: no matches found")
                cache[id] = str(status)
                continue
            path = matches[0]
            result = transcribe(path) if path else None

        transcripts[id] = {
            "title": title,
            "source": src_type,
            "transcript": result
        }
        cache[id] = "done"
        os.remove(path)

    update_cache(cache)
    with open("transcripts.json", "w") as f:
        json.dump(transcripts, f, indent = 4)

def check_cache(video_ids):
    """ returns cache state for each video ID to prevent unnecessary work """

    #TODO: this function works together with update_cache and is currently being saved and fetched via JSON
    #      in the future probably migrate to a SQL or some other database

    results = {}
    cache = load_json("cache.json", {})
        
    for id in video_ids:
        results[id] = cache.get(id, "0")

    return results

def update_cache(states):
    """ stores cache state for each video ID to prevent unnecessary work """

    #TODO: this function works together with check_cache and is currently being saved and fetched via JSON
    #      in the future probably migrate to a SQL or some other database
    cache = load_json("cache.json", {})
    
    for state in states.keys():
        if state not in cache.keys() or cache[state] != states[state]:
            cache[state] = states[state]
    
    with open("cache.json", "w") as f:
        json.dump(cache, f, indent = 4)

def main():
    get_transcripts()

    return

if __name__ == "__main__":
    main()