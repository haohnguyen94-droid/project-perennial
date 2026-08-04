"""
Unit tests for FINRA Short Interest Fetcher (Task A / Card #12).
Uses unittest, mocks, and temporary fixtures to test without real network calls.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure development/backend/src is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "development" / "backend" / "src"))

from services.consensus_watchlist.fetchers.short_interest import (
    fetch_short_interest_record,
    get_candidate_tickers,
    load_existing_cache,
    normalize_ticker,
    parse_finra_record,
    run,
    save_atomic_json,
)


class TestShortInterestFetcher(unittest.TestCase):

    def test_ticker_normalization(self):
        self.assertEqual(normalize_ticker(" nvda "), "NVDA")
        self.assertEqual(normalize_ticker("aapl"), "AAPL")
        self.assertIsNone(normalize_ticker("N/A"))
        self.assertIsNone(normalize_ticker(""))
        self.assertIsNone(normalize_ticker(None))
        self.assertIsNone(normalize_ticker("--"))

    def test_candidate_union_construction(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            congress_file = tmp_path / "trades_congress.json"
            ark_file = tmp_path / "ark_holdings.json"

            # Create mock congress trades file
            congress_data = {
                "trades": [
                    {"ticker": "NVDA", "trade_type": "Purchase"},
                    {"ticker": "AAPL", "trade_type": "Purchase"},
                    {"ticker": "N/A", "trade_type": "Purchase"},
                ]
            }
            with open(congress_file, "w", encoding="utf-8") as f:
                json.dump(congress_data, f)

            # Create mock ark holdings file
            ark_data = {
                "holdings": [
                    {"ticker": "aapl"},
                    {"ticker": "TSLA"},
                ]
            }
            with open(ark_file, "w", encoding="utf-8") as f:
                json.dump(ark_data, f)

            candidates = get_candidate_tickers(congress_file, ark_file)
            self.assertEqual(candidates, ["AAPL", "NVDA", "TSLA"])

    def test_valid_finra_response_parsing(self):
        raw = {
            "currentShortPositionQuantity": 45230000,
            "averageDailyVolumeQuantity": 19665000,
            "daysToCoverQuantity": 2.3,
            "settlementDate": "2026-05-01",
            "revisionFlag": "N",
        }
        parsed = parse_finra_record("nvda", raw)
        self.assertEqual(parsed["ticker"], "NVDA")
        self.assertEqual(parsed["short_position_shares"], 45230000)
        self.assertEqual(parsed["average_daily_volume"], 19665000)
        self.assertEqual(parsed["days_to_cover"], 2.3)
        self.assertEqual(parsed["settlement_date"], "2026-05-01")
        self.assertEqual(parsed["revision_flag"], "N")
        self.assertEqual(parsed["data_source"], "finra")
        self.assertIn("fetched_at", parsed)

    def test_null_fields_preservation(self):
        raw = {
            "currentShortPositionQuantity": 1000,
            "averageDailyVolumeQuantity": None,
            "daysToCoverQuantity": None,
            "settlementDate": "2026-05-01",
            "revisionFlag": None,
        }
        parsed = parse_finra_record("XYZ", raw)
        self.assertEqual(parsed["short_position_shares"], 1000)
        self.assertIsNone(parsed["average_daily_volume"])
        self.assertIsNone(parsed["days_to_cover"])
        self.assertIsNone(parsed["revision_flag"])

    def test_revised_records(self):
        raw = {
            "currentShortPositionQuantity": 5000,
            "revisionFlag": "Y",
            "settlementDate": "2026-05-15",
        }
        parsed = parse_finra_record("ABC", raw)
        self.assertEqual(parsed["revision_flag"], "Y")
        self.assertEqual(parsed["settlement_date"], "2026-05-15")

    @patch("requests.Session.get")
    def test_http_failure_and_retries(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.raise_for_status.side_effect = Exception("Internal Server Error")
        mock_get.return_value = mock_resp

        record, err = fetch_short_interest_record("FAIL")
        self.assertIsNone(record)
        self.assertIsNotNone(err)
        self.assertIn("Internal Server Error", err)

    @patch("requests.Session.get")
    def test_malformed_response_handling(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.side_effect = json.JSONDecodeError("Expecting value", "", 0)
        mock_get.return_value = mock_resp

        record, err = fetch_short_interest_record("BADJSON")
        self.assertIsNone(record)
        self.assertIsNotNone(err)
        self.assertIn("Malformed response", err)

    def test_atomic_output_behavior(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target_path = Path(tmpdir) / "sub" / "short_interest.json"
            test_data = {"schema_version": "1.0", "records": [{"ticker": "TEST"}]}

            save_atomic_json(test_data, [target_path])
            self.assertTrue(target_path.exists())

            with open(target_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            self.assertEqual(loaded["records"][0]["ticker"], "TEST")

    def test_cache_loading_and_skip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_file = Path(tmpdir) / "short_interest.json"
            cached_data = {
                "records": [
                    {
                        "ticker": "NVDA",
                        "short_position_shares": 100,
                        "days_to_cover": 1.5,
                        "settlement_date": "2026-05-01",
                    }
                ]
            }
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cached_data, f)

            cache = load_existing_cache(cache_file)
            self.assertIn("NVDA", cache)
            self.assertEqual(cache["NVDA"]["short_position_shares"], 100)


if __name__ == "__main__":
    unittest.main()
