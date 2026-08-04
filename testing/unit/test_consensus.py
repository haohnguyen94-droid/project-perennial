"""
Unit tests for Consensus Watchlist Aggregator (Task B / Card #13).
Uses unittest, mocks, and temporary JSON fixtures.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# Ensure development/backend/src is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "development" / "backend" / "src"))

from services.consensus_watchlist.consensus import (
    MARKET_CAP_THRESHOLD,
    affordable_growing_sort_key,
    load_ark_signals,
    load_congress_signals,
    load_insider_signals,
    load_short_interest_signals,
    popular_stable_sort_key,
    run,
)


class TestConsensusAggregator(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.tmppath = Path(self.tmpdir.name)

        self.congress_file = self.tmppath / "trades_congress.json"
        self.ark_file = self.tmppath / "ark_holdings.json"
        self.insider_file = self.tmppath / "trades_insider.json"
        self.si_file = self.tmppath / "short_interest.json"

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_congress_only_ticker(self):
        congress_data = {
            "trades": [
                {
                    "ticker": "NVDA",
                    "trade_type": "Purchase",
                    "politician_name": "John Doe",
                    "transaction_date": "2026-05-12",
                    "disclosure_date": "2026-06-10",
                    "amount_range": "$50,001 - $100,000",
                }
            ]
        }
        with open(self.congress_file, "w", encoding="utf-8") as f:
            json.dump(congress_data, f)

        # Profile cache mocking market cap > $10B
        profile_cache = {"NVDA": 2_000_000_000_000.0}

        result = run(
            congress_file=self.congress_file,
            ark_file=self.ark_file,
            insider_file=self.insider_file,
            short_interest_file=self.si_file,
            profile_cache=profile_cache,
        )

        self.assertEqual(len(result["popular_stable"]), 1)
        item = result["popular_stable"][0]
        self.assertEqual(item["ticker"], "NVDA")
        self.assertEqual(item["bucket"], "popular_stable")
        self.assertEqual(item["rank"], 1)
        self.assertIsNotNone(item["signals"]["congress"])
        self.assertIsNone(item["signals"]["ark"])
        self.assertIsNone(item["signals"]["insider"])
        self.assertIsNone(item["signals"]["short_interest"])

    def test_ark_only_ticker(self):
        ark_data = {
            "fetched_at": "2026-05-01T00:00:00Z",
            "holdings": [
                {
                    "ticker": "ROKU",
                    "company": "Roku Inc",
                    "funds": ["ARKK"],
                    "fund_count": 1,
                    "total_weight": 5.2,
                    "share_price": 60.0,
                }
            ],
        }
        with open(self.ark_file, "w", encoding="utf-8") as f:
            json.dump(ark_data, f)

        profile_cache = {"ROKU": 8_000_000_000.0}  # < $10B -> affordable_growing

        result = run(
            congress_file=self.congress_file,
            ark_file=self.ark_file,
            insider_file=self.insider_file,
            short_interest_file=self.si_file,
            profile_cache=profile_cache,
        )

        self.assertEqual(len(result["affordable_growing"]), 1)
        item = result["affordable_growing"][0]
        self.assertEqual(item["ticker"], "ROKU")
        self.assertEqual(item["bucket"], "affordable_growing")
        self.assertIsNotNone(item["signals"]["ark"])
        self.assertIsNone(item["signals"]["congress"])

    def test_ticker_in_both_sources_and_all_signals(self):
        congress_data = {
            "trades": [
                {
                    "ticker": "AAPL",
                    "trade_type": "Purchase",
                    "politician_name": "Jane Smith",
                    "transaction_date": "2026-05-10",
                    "disclosure_date": "2026-06-01",
                    "amount_range": "$15,001 - $50,000",
                }
            ]
        }
        ark_data = {
            "fetched_at": "2026-05-01T00:00:00Z",
            "holdings": [
                {
                    "ticker": "AAPL",
                    "company": "Apple Inc",
                    "funds": ["ARKK", "ARKW"],
                    "fund_count": 2,
                    "total_weight": 10.0,
                    "share_price": 180.0,
                }
            ],
        }
        insider_data = {
            "transactions": [
                {
                    "ticker": "AAPL",
                    "transaction_type": "Purchase",
                    "insider_name": "Tim Cook",
                    "value": 500000,
                    "transaction_date": "2026-05-15",
                }
            ]
        }
        si_data = {
            "records": [
                {
                    "ticker": "AAPL",
                    "short_position_shares": 10000000,
                    "average_daily_volume": 50000000,
                    "days_to_cover": 0.2,
                    "settlement_date": "2026-05-01",
                }
            ]
        }

        with open(self.congress_file, "w", encoding="utf-8") as f:
            json.dump(congress_data, f)
        with open(self.ark_file, "w", encoding="utf-8") as f:
            json.dump(ark_data, f)
        with open(self.insider_file, "w", encoding="utf-8") as f:
            json.dump(insider_data, f)
        with open(self.si_file, "w", encoding="utf-8") as f:
            json.dump(si_data, f)

        profile_cache = {"AAPL": 3_000_000_000_000.0}

        result = run(
            congress_file=self.congress_file,
            ark_file=self.ark_file,
            insider_file=self.insider_file,
            short_interest_file=self.si_file,
            profile_cache=profile_cache,
        )

        self.assertEqual(len(result["popular_stable"]), 1)
        item = result["popular_stable"][0]
        self.assertEqual(item["ticker"], "AAPL")
        self.assertIsNotNone(item["signals"]["congress"])
        self.assertIsNotNone(item["signals"]["ark"])
        self.assertIsNotNone(item["signals"]["insider"])
        self.assertIsNotNone(item["signals"]["short_interest"])
        self.assertEqual(item["source_dates"]["congress"], "2026-06-01")
        self.assertEqual(item["source_dates"]["insider"], "2026-05-15")
        self.assertEqual(item["source_dates"]["short_interest"], "2026-05-01")

    def test_missing_market_cap_placed_in_unresolved(self):
        congress_data = {
            "trades": [
                {"ticker": "UNKNOWN", "trade_type": "Purchase", "politician_name": "Bob"}
            ]
        }
        with open(self.congress_file, "w", encoding="utf-8") as f:
            json.dump(congress_data, f)

        profile_cache = {"UNKNOWN": None}  # Market cap missing

        result = run(
            congress_file=self.congress_file,
            ark_file=self.ark_file,
            insider_file=self.insider_file,
            short_interest_file=self.si_file,
            profile_cache=profile_cache,
        )

        self.assertEqual(len(result["unresolved"]), 1)
        item = result["unresolved"][0]
        self.assertEqual(item["ticker"], "UNKNOWN")
        self.assertEqual(item["bucket"], "unresolved")
        self.assertIsNone(item["rank"])
        self.assertIn("market_cap_unavailable", item["warnings"])

    def test_market_cap_threshold_boundary(self):
        congress_data = {
            "trades": [
                {"ticker": "EXACT10B", "trade_type": "Purchase", "politician_name": "Alice"},
                {"ticker": "OVER10B", "trade_type": "Purchase", "politician_name": "Bob"},
            ]
        }
        with open(self.congress_file, "w", encoding="utf-8") as f:
            json.dump(congress_data, f)

        profile_cache = {
            "EXACT10B": 10_000_000_000.0,  # <= $10B -> affordable_growing
            "OVER10B": 10_000_000_001.0,   # > $10B -> popular_stable
        }

        result = run(
            congress_file=self.congress_file,
            ark_file=self.ark_file,
            insider_file=self.insider_file,
            short_interest_file=self.si_file,
            profile_cache=profile_cache,
        )

        self.assertEqual(len(result["popular_stable"]), 1)
        self.assertEqual(result["popular_stable"][0]["ticker"], "OVER10B")

        self.assertEqual(len(result["affordable_growing"]), 1)
        self.assertEqual(result["affordable_growing"][0]["ticker"], "EXACT10B")

    def test_duplicate_congressional_transactions(self):
        congress_data = {
            "trades": [
                {"ticker": "NVDA", "trade_type": "Purchase", "politician_name": "Pol A", "transaction_date": "2026-05-01"},
                {"ticker": "NVDA", "trade_type": "Purchase", "politician_name": "Pol A", "transaction_date": "2026-05-02"},
                {"ticker": "NVDA", "trade_type": "Purchase", "politician_name": "Pol B", "transaction_date": "2026-05-03"},
            ]
        }
        with open(self.congress_file, "w", encoding="utf-8") as f:
            json.dump(congress_data, f)

        profile_cache = {"NVDA": 50_000_000_000.0}

        result = run(
            congress_file=self.congress_file,
            ark_file=self.ark_file,
            insider_file=self.insider_file,
            short_interest_file=self.si_file,
            profile_cache=profile_cache,
        )

        item = result["popular_stable"][0]
        self.assertEqual(item["signals"]["congress"]["buy_count"], 3)
        self.assertEqual(item["signals"]["congress"]["distinct_buyer_count"], 2)

    def test_deterministic_ranking_and_tie_breaker(self):
        # Two tickers with equal metrics sorted alphabetically A-Z
        congress_data = {
            "trades": [
                {"ticker": "ZZZ", "trade_type": "Purchase", "politician_name": "Pol A"},
                {"ticker": "AAA", "trade_type": "Purchase", "politician_name": "Pol A"},
            ]
        }
        with open(self.congress_file, "w", encoding="utf-8") as f:
            json.dump(congress_data, f)

        profile_cache = {"AAA": 20_000_000_000.0, "ZZZ": 20_000_000_000.0}

        result = run(
            congress_file=self.congress_file,
            ark_file=self.ark_file,
            insider_file=self.insider_file,
            short_interest_file=self.si_file,
            profile_cache=profile_cache,
        )

        tickers = [r["ticker"] for r in result["popular_stable"]]
        self.assertEqual(tickers, ["AAA", "ZZZ"])
        self.assertEqual(result["popular_stable"][0]["rank"], 1)
        self.assertEqual(result["popular_stable"][1]["rank"], 2)

    def test_invalid_input_file_handling(self):
        # Write corrupted JSON to congress file
        with open(self.congress_file, "w", encoding="utf-8") as f:
            f.write("corrupted json {")

        result = run(
            congress_file=self.congress_file,
            ark_file=self.ark_file,
            insider_file=self.insider_file,
            short_interest_file=self.si_file,
            profile_cache={},
        )

        # Pipeline completes gracefully without crashing
        self.assertIn("popular_stable", result)
        self.assertIn("affordable_growing", result)
        self.assertIn("unresolved", result)


if __name__ == "__main__":
    unittest.main()
