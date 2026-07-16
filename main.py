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
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window

# Kivyのデフォルトフォント("Roboto")には日本語グリフが含まれていないため、
# 日本語を入力/表示すると文字化け(豆腐)になる。
# ここで "Roboto" という名前そのものを日本語対応フォントで上書き登録することで、
# 個々のkvルールを一切変更せずにアプリ全体を日本語対応にする。
_FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts", "Kosugi-Regular.ttf")
if os.path.exists(_FONT_PATH):
    LabelBase.register(name="Roboto", fn_regular=_FONT_PATH, fn_bold=_FONT_PATH)

from data.storage import HabitStore
from screens.home_screen import HomeScreen
from screens.add_habit_screen import AddHabitScreen
from screens.stats_screen import StatsScreen
from screens.garden_screen import GardenScreen
from screens.recap_screen import RecapScreen


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
        sm.add_widget(GardenScreen(name="garden"))
        sm.add_widget(RecapScreen(name="recap"))
        sm.current = "home"
        return sm

    @staticmethod
    def _is_mobile_platform() -> bool:
        from kivy.utils import platform

        return platform in ("android", "ios")


if __name__ == "__main__":
    HabitGraphApp().run()
