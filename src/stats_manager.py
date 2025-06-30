import json
import logging
import os

# from gettext import gettext as _
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class StatsManager:
    def __init__(self, stats_file: str = os.path.join(path, "data", "meals.json")):
        self.log = logger.error
        self.stats_file = stats_file
        self.stats: list[dict] = []
        self._load_stats()

    def _load_stats(self):
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, encoding="utf-8") as f:
                    self.stats = json.load(f)
            except Exception as e:
                self.log(f"Ошибка при загрузке: {e}")
                self.stats = []
        else:
            self.stats = []

    def _save_stats(self):
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        with open(self.stats_file, "w", encoding="utf-8") as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=4)

    def log_product_usage(self, items: list[dict], total: float):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "items": items,
            "total": total,
        }
        self.stats.append(entry)
        self._save_stats()

    def _is_within_range(self, timestamp: str, start: datetime, end: datetime) -> bool:
        try:
            dt = datetime.fromisoformat(timestamp)
            return start <= dt <= end
        except Exception:
            return False

    def get_stats_for_range(self, start_date: str, end_date: str) -> list[dict]:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return [
            entry
            for entry in self.stats
            if self._is_within_range(entry["timestamp"], start, end)
        ]

    def get_stats_last_n_days(self, n: int) -> list[dict]:
        today = datetime.now()
        start = today - timedelta(days=n - 1)
        return self.get_stats_for_range(
            start.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")
        )

    def get_stats_by_period(self, period: str) -> list[dict]:
        if period == "week":
            return self.get_stats_last_n_days(7)
        elif period == "month":
            return self.get_stats_last_n_days(30)
        elif period == "all":
            return self.stats
        else:
            msg = _("Неизвестный период: {period}").format(period=period)
            self.log(msg)
            raise ValueError(msg)

    def clear_stats(self):
        self.stats = []
        self._save_stats()
