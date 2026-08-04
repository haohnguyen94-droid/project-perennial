"""
RE-EXPORT / ALIAS:
    Forwards consensus watchlist calls to consensus.py located at:
    development/backend/src/services/consensus_watchlist/consensus.py
"""

from ..consensus import run, popular_stable_sort_key, affordable_growing_sort_key

if __name__ == "__main__":
    run()
