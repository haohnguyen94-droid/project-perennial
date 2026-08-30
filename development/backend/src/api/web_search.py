import argparse
from src.utils.youtube_logger import create_logger
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BACKEND_DIR/"data"
DATA_DIR.mkdir(exist_ok=True)
GOOGLE_URL_PREFIX = "https://www.google.com/search"
SEARCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:154.0) "
        "Gecko/20100101 Firefox/154.0"
    )
}

def clean_google_url(href: str) -> str | None:
    """
    Return the external destination URL, or None if the link
    should not be included.
    """
    if href.startswith("/url?"):
        parsed = urlparse(href)
        parameters = parse_qs(parsed.query)
        href = parameters.get("q", [None])[0]

    if not href:
        return None

    parsed = urlparse(href)

    if parsed.scheme not in {"http", "https"}:
        return None

    # Exclude links pointing back to Google.
    if "google." in parsed.netloc.lower():
        return None

    return href

def get_top_urls(phrase: str, logger):
    res = requests.get(
        GOOGLE_URL_PREFIX,
        params={
            "q": phrase,
            "num": 10,
            "hl": "en",
            "gl": "us",
        },
        headers=SEARCH_HEADERS,
        timeout=10,
    )

    logger.info(f"Web Engine status code for \"{phrase}\": {res.status_code}")
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    results = []
    seen = set()

    for heading in soup.find_all("h3"):
        link = heading.find_parent("a")
        if link is None:
           continue
        href = link.get("href")
        cleaned_url = clean_google_url(href or "")

        if cleaned_url is None or cleaned_url in seen:
            continue

        seen.add(cleaned_url)
        results.append(cleaned_url)
        logger.info(f"added url: {cleaned_url}")

        if len(results) >= 10:
            break
    return results

def handle_urls(url_list, filepath, logger):
    for url in url_list:
        # visit url and parse out the information and save to filepath
        continue

    return

def main():
    parser = argparse.ArgumentParser(
    description="Return top data from search results from a web engine given search term."
    )
    parser.add_argument(
        "phrase",
        help="phrase to search for"
    )
    args = parser.parse_args()
    phrase = args.phrase
    print(f"Searching for: {phrase}")

    search_result_file = f"{DATA_DIR}/{phrase}_results.json"
    
  
    logger = create_logger(phrase+".log")
    url_list = get_top_urls(phrase, logger)

    if not url_list:
        logger.warning("No valid URLs found")
        return
    
    handle_urls(url_list, search_result_file, logger)
    
    return


if __name__ == "__main__":
    main()