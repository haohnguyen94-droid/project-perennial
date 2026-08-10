## Setup

1. create virtual environment
2. run `pip install -r requirements.txt` to download import dependencies
3. **_Optional_** Running the youtube.py script will throw some warnings that are mostly harmless for now. You can reduce the warnings by installing Deno and FFMPEG
   - in cmd run `winget install DenoLand.Deno` and verify with `deno --version`
   - in cmd run `winget install Gyan.FFmpeg` and verify with `ffmpeg -version`

## Use

1. First go project-perennual/development/backend/cloudflare-worker
2. Run npm run deploy command to ensure cloudflare worker is ready to take requests
3. Change directory to project-perennial/development/backend
4. Run the command python -m src.api.youtube "<search term>"

## Outputs

After you run youtube.py some new files should be created:

- status.json - holds the status states of each video id. The states can be: Done, 1-3 for a maximum of 3 retries per ID before we abandon
- metadata.json - this holds a list of all video IDs along with the video title and which channel the video came from
- transcripts.json - this holds the actual transcript of each fetched video if it was successful or a None object if unsuccessful

## TODOs

In the main function there only the get_transcript() function is being called because a dummy data.json is saved so we can lower the API calls for testing. If you would like to check out videos related to other keywords you would need to call get_videos() with a keyword/phrase.

Currently the script only loops through the first 5 elements. Further testing needs to be done to check on the behavior of the script with heavier request loads.

While the option to get video audio and get transcript via whisper that feature has not been tested yet. I have yet encountered any video that doesn't have either manually uploaded transcript or auto generated transcripts.
