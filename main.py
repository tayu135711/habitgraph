"""
HabitGraph
-----------
シンプルな習慣トラッカー・スマホアプリ(Kivy製)。

- 習慣を登録して毎日チェック
- 連続達成日数(ストリーク)を自動計算
- 直近7日間の達成状況を棒グラフで可視化
- データはJSONでローカル保存(サーバー不要・オフライン動作)

Buildozerでそのまま Android の .apk / iOS 向けにビルドできる構成。
"""
import os

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

from data.storage import HabitStore
from screens.home_screen import HomeScreen
from screens.add_habit_screen import AddHabitScreen
from screens.stats_screen import StatsScreen


class HabitGraphApp(App):
    def build(self):
        self.title = "HabitGraph"
        Window.clearcolor = (0.06, 0.07, 0.09, 1)

        # デスクトップでの動作確認用にスマホっぽい縦長ウィンドウサイズにする。
        # 実機(Android/iOS)ではOS側が画面サイズを制御するため無視される。
        if not self._is_mobile_platform():
            Window.size = (390, 780)

        storage_path = os.path.join(self.user_data_dir, "habits.json")
        self.store = HabitStore(storage_path)

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AddHabitScreen(name="add_habit"))
        sm.add_widget(StatsScreen(name="stats"))
        sm.current = "home"
        return sm

    @staticmethod
    def _is_mobile_platform() -> bool:
        from kivy.utils import platform

        return platform in ("android", "ios")


if __name__ == "__main__":
    HabitGraphApp().run()
