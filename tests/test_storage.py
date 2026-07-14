"""
data.storage のユニットテスト。
Kivy(GUI)に依存しないロジック部分だけを対象にしているので、
CI環境でも Xvfb 無しで高速に実行できる。
"""
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.storage import HabitStore, today_str  # noqa: E402


def make_store(tmp_path) -> HabitStore:
    return HabitStore(tmp_path / "habits.json")


def test_add_habit(tmp_path):
    store = make_store(tmp_path)
    h = store.add_habit("  Read  ", "#4F8EF7")
    assert h.name == "Read"
    assert h.id in store.habits
    assert (tmp_path / "habits.json").exists()


def test_toggle_today(tmp_path):
    store = make_store(tmp_path)
    h = store.add_habit("Exercise", "#22C55E")
    assert h.is_done_on(today_str()) is False

    result = store.toggle_today(h.id)
    assert result is True
    assert store.habits[h.id].is_done_on(today_str()) is True

    result2 = store.toggle_today(h.id)
    assert result2 is False


def test_persistence_reload(tmp_path):
    path = tmp_path / "habits.json"
    store1 = HabitStore(path)
    h = store1.add_habit("Meditate", "#A855F7")
    store1.toggle_today(h.id)

    store2 = HabitStore(path)  # reload from disk
    assert len(store2.habits) == 1
    reloaded = store2.habits[h.id]
    assert reloaded.name == "Meditate"
    assert reloaded.is_done_on(today_str()) is True


def test_current_streak(tmp_path):
    store = make_store(tmp_path)
    h = store.add_habit("Walk", "#F97316")

    today = date.today()
    for i in range(5):
        h.logs[(today - timedelta(days=i)).strftime("%Y-%m-%d")] = True
    # break the streak 6 days ago
    h.logs[(today - timedelta(days=6)).strftime("%Y-%m-%d")] = True

    assert h.current_streak(today) == 5


def test_last_n_days_order(tmp_path):
    store = make_store(tmp_path)
    h = store.add_habit("Stretch", "#EAB308")
    today = date.today()
    h.logs[today.strftime("%Y-%m-%d")] = True

    days = h.last_n_days(3, ref_day=today)
    assert len(days) == 3
    # 最後の要素が「今日」であること(古い順に並んでいる)
    assert days[-1][0] == today.strftime("%m/%d")
    assert days[-1][1] is True


def test_overall_today_rate(tmp_path):
    store = make_store(tmp_path)
    h1 = store.add_habit("A", "#4F8EF7")
    store.add_habit("B", "#22C55E")

    assert store.overall_today_rate() == 0.0
    store.toggle_today(h1.id)
    assert store.overall_today_rate() == 0.5


def test_delete_habit(tmp_path):
    store = make_store(tmp_path)
    h = store.add_habit("Temp", "#EF4444")
    store.delete_habit(h.id)
    assert h.id not in store.habits
