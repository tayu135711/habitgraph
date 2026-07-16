"""
habitgraph.screens.home_screen
---------------------------------
アプリ起動時に表示されるメイン画面。
今日の達成率(リング)と、習慣ごとのチェックリストを表示する。
"""
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.metrics import dp
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
                on_delete=self.confirm_delete_habit,
            )
            self.habit_list.add_widget(card)

        self.ring.progress = store.overall_today_rate()

    def toggle_habit(self, habit_id: str):
        store = App.get_running_app().store
        store.toggle_today(habit_id)
        self.refresh()

    def confirm_delete_habit(self, habit_id: str, habit_name: str):
        """削除前に一度確認ダイアログを挟む(誤タップ対策)"""
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(16))
        content.add_widget(
            Label(text=f'"{habit_name}" を削除しますか?\n記録も全て消えます。', halign="center")
        )

        buttons = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(12))
        cancel_btn = Button(text="キャンセル")
        delete_btn = Button(text="削除する")
        buttons.add_widget(cancel_btn)
        buttons.add_widget(delete_btn)
        content.add_widget(buttons)

        popup = Popup(
            title="習慣の削除",
            content=content,
            size_hint=(0.8, 0.35),
            auto_dismiss=False,
        )

        def do_delete(*_):
            store = App.get_running_app().store
            store.delete_habit(habit_id)
            popup.dismiss()
            self.refresh()

        cancel_btn.bind(on_release=popup.dismiss)
        delete_btn.bind(on_release=do_delete)
        popup.open()

    def go_add(self):
        self.manager.transition.direction = "left"
        self.manager.current = "add_habit"

    def go_stats(self):
        self.manager.transition.direction = "left"
        self.manager.current = "stats"

    def go_garden(self):
        self.manager.transition.direction = "left"
        self.manager.current = "garden"

    def go_recap(self):
        self.manager.transition.direction = "left"
        self.manager.current = "recap"


def _today(store):
    from data.storage import today_str

    return today_str()
