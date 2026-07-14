"""
habitgraph.data.storage
------------------------
Kivyに依存しない、純粋なPythonのデータ永続化レイヤー。
JSONファイルに習慣(habit)とその日々の達成記録(check-in)を保存する。

Kivyから切り離してあるのは、
  - ユニットテストがしやすい
  - 将来ストレージ実装(SQLite等)を差し替えやすい
ため。
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


DATE_FMT = "%Y-%m-%d"


def today_str() -> str:
    return date.today().strftime(DATE_FMT)


@dataclass
class Habit:
    id: str
    name: str
    color: str  # "#RRGGBB"
    created_at: str
    # {"2026-07-14": True, "2026-07-13": False, ...}
    logs: Dict[str, bool] = field(default_factory=dict)

    def is_done_on(self, day: str) -> bool:
        return self.logs.get(day, False)

    def toggle(self, day: str) -> bool:
        """指定日の達成状態をトグルして、トグル後の状態を返す"""
        new_state = not self.logs.get(day, False)
        self.logs[day] = new_state
        return new_state

    def current_streak(self, ref_day: Optional[date] = None) -> int:
        """今日(または基準日)から遡って連続達成日数を数える"""
        ref_day = ref_day or date.today()
        streak = 0
        cursor = ref_day
        while self.logs.get(cursor.strftime(DATE_FMT), False):
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def last_n_days(self, n: int = 7, ref_day: Optional[date] = None) -> List[tuple]:
        """[(label, done_bool), ...] を古い順に返す。グラフ描画用。"""
        ref_day = ref_day or date.today()
        days = []
        for i in range(n - 1, -1, -1):
            d = ref_day - timedelta(days=i)
            key = d.strftime(DATE_FMT)
            days.append((d.strftime("%m/%d"), self.logs.get(key, False)))
        return days

    def completion_rate(self, n: int = 7, ref_day: Optional[date] = None) -> float:
        days = self.last_n_days(n, ref_day)
        if not days:
            return 0.0
        done = sum(1 for _, ok in days if ok)
        return done / len(days)


class HabitStore:
    """習慣一覧をJSONファイルに永続化するリポジトリ"""

    def __init__(self, storage_path: str | Path):
        self.storage_path = Path(storage_path)
        self.habits: Dict[str, Habit] = {}
        self._load()

    # ---- persistence -------------------------------------------------
    def _load(self) -> None:
        if not self.storage_path.exists():
            self.habits = {}
            return
        try:
            raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            raw = {}
        self.habits = {
            hid: Habit(
                id=h["id"],
                name=h["name"],
                color=h["color"],
                created_at=h["created_at"],
                logs=h.get("logs", {}),
            )
            for hid, h in raw.items()
        }

    def save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {hid: asdict(h) for hid, h in self.habits.items()}
        self.storage_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ---- CRUD ----------------------------------------------------------
    def add_habit(self, name: str, color: str) -> Habit:
        hid = uuid.uuid4().hex[:8]
        habit = Habit(
            id=hid,
            name=name.strip(),
            color=color,
            created_at=today_str(),
        )
        self.habits[hid] = habit
        self.save()
        return habit

    def delete_habit(self, habit_id: str) -> None:
        self.habits.pop(habit_id, None)
        self.save()

    def toggle_today(self, habit_id: str) -> Optional[bool]:
        habit = self.habits.get(habit_id)
        if not habit:
            return None
        new_state = habit.toggle(today_str())
        self.save()
        return new_state

    def list_habits(self) -> List[Habit]:
        return sorted(self.habits.values(), key=lambda h: h.created_at)

    def overall_today_rate(self) -> float:
        habits = self.list_habits()
        if not habits:
            return 0.0
        done = sum(1 for h in habits if h.is_done_on(today_str()))
        return done / len(habits)
