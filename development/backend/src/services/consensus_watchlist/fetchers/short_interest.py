"""
PURPOSE:
    Fetches official FINRA consolidated Equity Short Interest data for tickers
    present in congress trades (trades_congress.json) and ARK holdings (ark_holdings.json).

CRITICAL DATA-SOURCE REQUIREMENT:
    Uses the FINRA consolidated Equity Short Interest dataset/API.
    Do NOT confuse FINRA daily short-sale volume (regsho daily download) with
    consolidated open short interest.

SOURCE:
    FINRA Consolidated Equity Short Interest API / Dataset
    Endpoint: https://api.finra.org/data/group/equity/service/shortInterest

SCHEDULE:
    Runs daily via scheduler/cron.py (after fmp.py and ark.py, before consensus.py)

OUTPUT:
    database/local_data/short_interest.json
"""

import json
import logging
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import requests
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────
# CONFIG & LOGGING
# ─────────────────────────────────────────────────────────

logger = logging.getLogger("short_interest")
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("[short_interest] %(levelname)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Load environment variables
dotenv_path = Path(__file__).resolve().parents[4] / ".env"
load_dotenv(dotenv_path=dotenv_path)

FINRA_API_URL = os.getenv(
    "FINRA_API_URL",
    "https://api.finra.org/data/group/equity/service/shortInterest"
)
FINRA_CLIENT_ID = os.getenv("FINRA_CLIENT_ID", "")
FINRA_CLIENT_SECRET = os.getenv("FINRA_CLIENT_SECRET", "")
FINRA_API_KEY = os.getenv("FINRA_API_KEY", "")

REQUEST_TIMEOUT_SECONDS = 15
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.0


# ─────────────────────────────────────────────────────────
# PATH HELPERS
# ─────────────────────────────────────────────────────────

def resolve_data_dirs() -> List[Path]:
    """
    Returns candidate database/local_data directories.
    Ensures directories exist.
    """
    curr = Path(__file__).resolve()
    project_root = None
    for p in [curr] + list(curr.parents):
        if p.name == "project-perennial" or (p / "development" / "backend").exists():
            project_root = p
            break
    if not project_root:
        project_root = curr.parents[5]

    candidates = [
        project_root / "development" / "database" / "local_data",
        project_root / "database" / "local_data",
    ]
    existing = []
    for d in candidates:
        d.mkdir(parents=True, exist_ok=True)
        if d not in existing:
            existing.append(d)
    return existing


def get_input_file_path(filename: str) -> Optional[Path]:
    """
    Finds existing input JSON file across potential data directories.
    """
    dirs = resolve_data_dirs()
    for d in dirs:
        p = d / filename
        if p.exists():
            return p
    return None


# ─────────────────────────────────────────────────────────
# CANDIDATE UNIVERSE
# ─────────────────────────────────────────────────────────

def normalize_ticker(ticker: str) -> Optional[str]:
    """
    Normalizes a ticker symbol consistently across fetchers.
    Strips whitespace and uppercase. Rejects invalid symbols.
    """
    if not ticker or not isinstance(ticker, str):
        return None
    cleaned = ticker.strip().upper()
    if not cleaned or cleaned in ("N/A", "NONE", "NULL", "--", "NAN"):
        return None
    return cleaned


def get_candidate_tickers(
    congress_file: Optional[Path] = None,
    ark_file: Optional[Path] = None
) -> List[str]:
    """
    Builds a deduplicated, normalized union of candidate tickers from:
      - database/local_data/trades_congress.json
      - database/local_data/ark_holdings.json

    Only tickers present in these input files are included.
    Market-wide scanning is explicitly avoided.
    """
    candidates: Set[str] = set()

    # Load Congress tickers
    c_path = congress_file or get_input_file_path("trades_congress.json")
    if c_path and c_path.exists():
        try:
            with open(c_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            trades = data.get("trades", [])
            for t in trades:
                norm = normalize_ticker(t.get("ticker"))
                if norm:
                    candidates.add(norm)
            logger.info(f"Loaded candidate tickers from Congress trades")
        except Exception as e:
            logger.warning(f"Error loading Congress trades from {c_path}: {e}")

    # Load ARK tickers
    a_path = ark_file or get_input_file_path("ark_holdings.json")
    if a_path and a_path.exists():
        try:
            with open(a_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            holdings = data.get("holdings", [])
            for h in holdings:
                norm = normalize_ticker(h.get("ticker"))
                if norm:
                    candidates.add(norm)
            logger.info(f"Loaded candidate tickers from ARK holdings")
        except Exception as e:
            logger.warning(f"Error loading ARK holdings from {a_path}: {e}")

    sorted_candidates = sorted(candidates)
    logger.info(f"Total deduplicated candidate universe: {len(sorted_candidates)} tickers")
    return sorted_candidates


# ─────────────────────────────────────────────────────────
# FINRA PROVIDER / CLIENT BOUNDARY
# ─────────────────────────────────────────────────────────

def parse_finra_record(ticker: str, raw_item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parses a raw FINRA equity short interest record into canonical schema.
    Preserves null values without inventing zeros.
    """
    norm_ticker = normalize_ticker(ticker) or ticker

    # Short position shares
    short_pos = (
        raw_item.get("currentShortPositionQuantity")
        if raw_item.get("currentShortPositionQuantity") is not None
        else raw_item.get("shortPositionQuantity", raw_item.get("short_position_shares"))
    )
    if short_pos is not None:
        try:
            short_pos = int(short_pos)
        except (ValueError, TypeError):
            short_pos = None

    # Average daily volume
    adv = (
        raw_item.get("averageDailyVolumeQuantity")
        if raw_item.get("averageDailyVolumeQuantity") is not None
        else raw_item.get("averageDailyVolume", raw_item.get("average_daily_volume"))
    )
    if adv is not None:
        try:
            adv = int(adv)
        except (ValueError, TypeError):
            adv = None

    # Days to cover
    dtc = (
        raw_item.get("daysToCoverQuantity")
        if raw_item.get("daysToCoverQuantity") is not None
        else raw_item.get("daysToCover", raw_item.get("days_to_cover"))
    )
    if dtc is not None:
        try:
            dtc = float(dtc)
        except (ValueError, TypeError):
            dtc = None

    # Settlement date
    settlement = (
        raw_item.get("settlementDate") or
        raw_item.get("settlement_date")
    )
    if settlement:
        settlement = str(settlement).strip()
    else:
        settlement = None

    # Revision flag
    rev_flag = (
        raw_item.get("revisionFlag")
        if raw_item.get("revisionFlag") is not None
        else raw_item.get("revision_flag")
    )
    if rev_flag is not None:
        rev_flag = str(rev_flag).strip()

    return {
        "ticker": norm_ticker,
        "short_position_shares": short_pos,
        "average_daily_volume": adv,
        "days_to_cover": dtc,
        "settlement_date": settlement,
        "revision_flag": rev_flag,
        "data_source": "finra",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def fetch_short_interest_record(
    ticker: str,
    session: Optional[requests.Session] = None,
    api_url: str = FINRA_API_URL
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Fetches FINRA Equity Short Interest record for a single ticker.
    Implements bounded retries with exponential backoff and timeout handling.

    Returns (record_dict, error_message).
    """
    req_session = session or requests.Session()
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if FINRA_API_KEY:
        headers["Authorization"] = f"Bearer {FINRA_API_KEY}"

    params = {"symbolCode": ticker}

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = req_session.get(
                api_url,
                headers=headers,
                params=params,
                timeout=REQUEST_TIMEOUT_SECONDS
            )

            if resp.status_code == 404:
                return None, None  # Ticker simply has no record in dataset

            if resp.status_code == 429:
                logger.warning(f"Rate limited (429) on {ticker}, waiting before retry (attempt {attempt})")
                time.sleep(BACKOFF_FACTOR * (2 ** attempt))
                continue

            if resp.status_code in (401, 403):
                err = f"FINRA API HTTP {resp.status_code}: Unauthorized/Forbidden. Verify credentials."
                logger.error(f"{ticker}: {err}")
                return None, err

            resp.raise_for_status()
            data = resp.json()

            records = []
            if isinstance(data, list):
                records = data
            elif isinstance(data, dict):
                records = data.get("data", data.get("records", [data]))

            if records:
                first = records[0]
                return parse_finra_record(ticker, first), None

            return None, None

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {ticker} (attempt {attempt}/{MAX_RETRIES})")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error for {ticker} (attempt {attempt}/{MAX_RETRIES}): {e}")
        except Exception as e:
            err = f"Malformed response or parse error for {ticker}: {e}"
            logger.error(err)
            return None, err

        if attempt < MAX_RETRIES:
            time.sleep(BACKOFF_FACTOR * attempt)

    err_msg = f"Failed to fetch short interest for {ticker} after {MAX_RETRIES} attempts"
    logger.error(err_msg)
    return None, err_msg


# ─────────────────────────────────────────────────────────
# CACHING & ATOMIC I/O
# ─────────────────────────────────────────────────────────

def load_existing_cache(output_file: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """
    Loads existing short_interest.json cache indexed by ticker.
    """
    path = output_file or get_input_file_path("short_interest.json")
    if not path or not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("records", [])
        cache = {}
        for r in records:
            norm = normalize_ticker(r.get("ticker"))
            if norm:
                cache[norm] = r
        logger.info(f"Loaded {len(cache)} existing short interest records from cache")
        return cache
    except Exception as e:
        logger.warning(f"Failed to load cache from {path}: {e}")
        return {}


def save_atomic_json(data: Dict[str, Any], target_paths: List[Path]) -> None:
    """
    Writes data atomically to target JSON paths.
    Creates temporary file in target directory then renames to prevent partial file corruption.
    """
    for target in target_paths:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=target.parent, delete=False, encoding="utf-8") as tf:
            json.dump(data, tf, indent=2, ensure_ascii=False)
            temp_path = Path(tf.name)

        try:
            temp_path.replace(target)
            logger.info(f"Saved atomic output to {target}")
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise IOError(f"Failed atomic write to {target}: {e}") from e


# ─────────────────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────────────────

def run(
    congress_file: Optional[Path] = None,
    ark_file: Optional[Path] = None,
    force_refresh: bool = False
) -> Dict[str, Any]:
    """
    Main entry point for short interest fetcher.
    Executed daily via scheduler or manually.
    """
    logger.info("Starting FINRA Consolidated Short Interest fetcher...")

    candidate_tickers = get_candidate_tickers(congress_file, ark_file)
    existing_cache = load_existing_cache()

    records: List[Dict[str, Any]] = []
    errors: List[str] = []

    session = requests.Session()

    for ticker in candidate_tickers:
        if not force_refresh and ticker in existing_cache:
            records.append(existing_cache[ticker])
            continue

        record, err = fetch_short_interest_record(ticker, session=session)
        if record:
            records.append(record)
        elif err:
            errors.append(err)

    records.sort(key=lambda r: r["ticker"])

    output_payload = {
        "schema_version": "1.0",
        "source": "finra",
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "records": records,
        "errors": errors,
    }

    target_paths = [d / "short_interest.json" for d in resolve_data_dirs()]
    save_atomic_json(output_payload, target_paths)

    logger.info(f"Short Interest fetch complete. {len(records)} records, {len(errors)} errors.")
    return output_payload


if __name__ == "__main__":
    run()
