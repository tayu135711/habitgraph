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
from datetime import date, timedelta
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

    def total_completions(self) -> int:
        """この習慣が生涯で達成された合計回数"""
        return sum(1 for v in self.logs.values() if v)


# 育成要素(木)の成長段階。(必要な合計達成回数, 表示名) のしきい値テーブル。
# 数値は「厳しすぎず、かつすぐ最大まで行かない」ことを狙って決めた目安値。
GROWTH_STAGES = [
    (0, "seed"),
    (5, "sprout"),
    (15, "sapling"),
    (30, "young_tree"),
    (60, "full_tree"),
    (120, "blooming_tree"),
]


def growth_stage_for(total_completions: int) -> tuple[int, str]:
    """合計達成回数から (段階インデックス, 段階名) を返す"""
    stage_index = 0
    stage_name = GROWTH_STAGES[0][1]
    for i, (threshold, name) in enumerate(GROWTH_STAGES):
        if total_completions >= threshold:
            stage_index = i
            stage_name = name
    return stage_index, stage_name


def next_growth_threshold(total_completions: int) -> Optional[int]:
    """次の段階まであと何回か。既に最大段階なら None"""
    for threshold, _ in GROWTH_STAGES:
        if total_completions < threshold:
            return threshold - total_completions
    return None


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

    def total_completions(self) -> int:
        """全習慣を通じた生涯の合計達成回数(育成要素のレベル計算に使う)"""
        return sum(h.total_completions() for h in self.habits.values())

    def weekly_recap(self, ref_day: Optional[date] = None) -> dict:
        """直近7日間のサマリーを1つの辞書にまとめて返す(週間リキャップカード用)。

        - total_checks: 直近7日間の達成チェック数の合計
        - active_days: 1つ以上の習慣を達成した日数
        - best_streak: 直近7日基準で見た、全習慣中の最長ストリーク
        - top_habit: 直近7日間で最も達成率が高かった習慣(タイなら登録が早い方)
        """
        ref_day = ref_day or date.today()
        habits = self.list_habits()

        total_checks = 0
        per_day_any = [False] * 7
        best_streak = 0
        top_habit = None
        top_rate = -1.0

        for habit in habits:
            days = habit.last_n_days(7, ref_day)
            for i, (_, done) in enumerate(days):
                if done:
                    total_checks += 1
                    per_day_any[i] = True

            streak = habit.current_streak(ref_day)
            if streak > best_streak:
                best_streak = streak

            rate = habit.completion_rate(7, ref_day)
            if rate > top_rate:
                top_rate = rate
                top_habit = habit

        active_days = sum(1 for v in per_day_any if v)

        return {
            "total_checks": total_checks,
            "active_days": active_days,
            "best_streak": best_streak,
            "top_habit_name": top_habit.name if top_habit else None,
            "top_habit_rate": top_rate if top_habit else 0.0,
            "habit_count": len(habits),
        }
