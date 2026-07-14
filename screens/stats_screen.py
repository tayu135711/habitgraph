"""
habitgraph.screens.stats_screen
-----------------------------------
全習慣について、直近7日間の達成状況をバーチャートで並べる画面。
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import ObjectProperty
from kivy.metrics import dp
from kivy.app import App

from widgets.bar_chart import BarChart


class HabitStatRow(BoxLayout):
    """1習慣ぶんの「名前 + ストリーク + バーチャート」の行"""

    def __init__(self, habit, **kwargs):
        super().__init__(orientation="vertical", size_hint_y=None, height=dp(120), **kwargs)
        self.padding = (dp(12), dp(8))
        self.spacing = dp(4)

        header = BoxLayout(size_hint_y=None, height=dp(24))
        header.add_widget(
            Label(
                text=f"{habit.name}",
                halign="left",
                valign="middle",
                bold=True,
                color=(1, 1, 1, 1),
            )
        )
        header.add_widget(
            Label(
                text=f"🔥 {habit.current_streak()}日連続",
                halign="right",
                valign="middle",
                color=(0.7, 0.75, 0.85, 1),
                size_hint_x=0.6,
            )
        )
        self.add_widget(header)

        chart = BarChart(size_hint_y=None, height=dp(80))
        chart.data = habit.last_n_days(7)
        color = habit.color.lstrip("#")
        r, g, b = (int(color[i : i + 2], 16) / 255 for i in (0, 2, 4))
        chart.bar_color = [r, g, b, 1]
        self.add_widget(chart)


class StatsScreen(Screen):
    stat_list = ObjectProperty(None)

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        store = App.get_running_app().store
        self.stat_list.clear_widgets()
        for habit in store.list_habits():
            self.stat_list.add_widget(HabitStatRow(habit))

    def go_home(self):
        self.manager.transition.direction = "right"
        self.manager.current = "home"
