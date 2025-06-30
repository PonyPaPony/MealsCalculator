import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, mock_open, patch

import pytest

from stats_manager import StatsManager


@pytest.fixture
def sample_data():
    now = datetime.now()
    return [
        {
            "timestamp": (now - timedelta(days=1)).isoformat(),
            "items": [{"name": "apple"}],
            "total": 100,
        },
        {
            "timestamp": (now - timedelta(days=5)).isoformat(),
            "items": [{"name": "banana"}],
            "total": 200,
        },
    ]


@pytest.fixture
def stats_path(tmp_path):
    return tmp_path / "meals.json"


# ---------- _load_stats ----------
def test_load_stats_success(stats_path, sample_data):
    stats_json = json.dumps(sample_data, ensure_ascii=False, indent=4)
    with patch("builtins.open", mock_open(read_data=stats_json)):
        with patch("os.path.exists", return_value=True):
            sm = StatsManager(stats_file=str(stats_path))
            assert sm.stats == sample_data


def test_load_stats_file_not_found(stats_path):
    with patch("os.path.exists", return_value=False):
        sm = StatsManager(stats_file=str(stats_path))
        assert sm.stats == []


def test_load_stats_json_error(stats_path):
    with patch("builtins.open", mock_open(read_data="INVALID_JSON")):
        with patch("os.path.exists", return_value=True):
            sm = StatsManager(stats_file=str(stats_path))
            assert sm.stats == []


# ---------- _save_stats ----------
def test_save_stats(stats_path, sample_data):
    sm = StatsManager(stats_file=str(stats_path))
    sm.stats = sample_data

    with patch("builtins.open", mock_open()) as m:
        sm._save_stats()
        m.assert_called_once_with(str(stats_path), "w", encoding="utf-8")


# ---------- log_product_usage ----------
def test_log_product_usage(stats_path):
    sm = StatsManager(stats_file=str(stats_path))
    sm._save_stats = MagicMock()
    before_len = len(sm.stats)
    sm.log_product_usage([{"name": "bread"}], 123.45)
    assert len(sm.stats) == before_len + 1
    sm._save_stats.assert_called_once()


# ---------- _is_within_range ----------
def test_is_within_range_valid():
    sm = StatsManager(stats_file="dummy.json")
    now = datetime.now()
    timestamp = now.isoformat()
    assert sm._is_within_range(
        timestamp, now - timedelta(minutes=1), now + timedelta(minutes=1)
    )


def test_is_within_range_invalid():
    sm = StatsManager(stats_file="dummy.json")
    assert not sm._is_within_range("invalid-timestamp", datetime.now(), datetime.now())


# ---------- get_stats_for_range ----------
def test_get_stats_for_range(stats_path, sample_data):
    sm = StatsManager(stats_file=str(stats_path))
    sm.stats = sample_data
    today = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    result = sm.get_stats_for_range(start, today)
    assert len(result) == len(sample_data)


# ---------- get_stats_last_n_days ----------
def test_get_stats_last_n_days(stats_path, sample_data):
    sm = StatsManager(stats_file=str(stats_path))
    sm.stats = sample_data
    result = sm.get_stats_last_n_days(7)
    assert len(result) == 2


# ---------- get_stats_by_period ----------
def test_get_stats_by_period_all(stats_path, sample_data):
    sm = StatsManager(stats_file=str(stats_path))
    sm.stats = sample_data
    assert sm.get_stats_by_period("all") == sample_data


def test_get_stats_by_period_week(stats_path, sample_data):
    sm = StatsManager(stats_file=str(stats_path))
    sm.stats = sample_data
    result = sm.get_stats_by_period("week")
    assert isinstance(result, list)


def test_get_stats_by_period_month(stats_path, sample_data):
    sm = StatsManager(stats_file=str(stats_path))
    sm.stats = sample_data
    result = sm.get_stats_by_period("month")
    assert isinstance(result, list)


def test_get_stats_by_period_unknown(stats_path):
    sm = StatsManager(stats_file=str(stats_path))
    with pytest.raises(ValueError):
        sm.get_stats_by_period("year")


# ---------- clear_stats ----------
def test_clear_stats(stats_path, sample_data):
    sm = StatsManager(stats_file=str(stats_path))
    sm.stats = sample_data
    sm._save_stats = MagicMock()
    sm.clear_stats()
    assert sm.stats == []
    sm._save_stats.assert_called_once()
