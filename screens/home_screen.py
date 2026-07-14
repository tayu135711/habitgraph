"""
habitgraph.screens.home_screen
---------------------------------
アプリ起動時に表示されるメイン画面。
今日の達成率(リング)と、習慣ごとのチェックリストを表示する。
"""
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.app import App

from widgets.habit_card import HabitCard


class HomeScreen(Screen):
    habit_list = ObjectProperty(None)  # kvの id="habit_list" (BoxLayout) を紐づけ
    ring = ObjectProperty(None)        # kvの id="ring" (RingProgress) を紐づけ

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        store = App.get_running_app().store
        self.habit_list.clear_widgets()

        habits = store.list_habits()
        if not habits:
            return

        for habit in habits:
            card = HabitCard(
                habit_id=habit.id,
                habit_name=habit.name,
                habit_color=habit.color,
                streak=habit.current_streak(),
                done_today=habit.is_done_on(_today(store)),
                on_toggle=self.toggle_habit,
            )
            self.habit_list.add_widget(card)

        self.ring.progress = store.overall_today_rate()

    def toggle_habit(self, habit_id: str):
        store = App.get_running_app().store
        store.toggle_today(habit_id)
        self.refresh()

    def go_add(self):
        self.manager.transition.direction = "left"
        self.manager.current = "add_habit"

    def go_stats(self):
        self.manager.transition.direction = "left"
        self.manager.current = "stats"


def _today(store):
    from data.storage import today_str

    return today_str()
