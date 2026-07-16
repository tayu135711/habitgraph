"""
habitgraph.screens.recap_screen
-----------------------------------
直近7日間のサマリーを1枚のカードにまとめて見せる画面。
週の終わりに「今週どれだけ積み重ねたか」を振り返れるようにする。
画像として端末に保存し、あとでギャラリーアプリ等から共有できる。
"""
import os

from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.utils import platform


class RecapScreen(Screen):
    card = ObjectProperty(None)  # 画像として書き出す対象のウィジェット

    total_checks = NumericProperty(0)
    active_days = NumericProperty(0)
    best_streak = NumericProperty(0)
    top_habit_name = StringProperty("-")
    save_status = StringProperty("")

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        store = App.get_running_app().store
        recap = store.weekly_recap()

        self.total_checks = recap["total_checks"]
        self.active_days = recap["active_days"]
        self.best_streak = recap["best_streak"]
        self.top_habit_name = recap["top_habit_name"] or "-"
        self.save_status = ""

    def _export_dir(self) -> str:
        """
        画像の保存先ディレクトリを返す。

        app.user_data_dir はアプリ専用の"内部"ストレージで、他のアプリ
        (ファイルマネージャー・ギャラリー等)からは基本的に見えない。
        「保存してあとで共有できる」ようにするには、権限リクエスト不要で
        書き込める"アプリ専用の外部ストレージ"(Android/data/<package>/files/...)
        を使う必要がある。デスクトップ(検証環境)ではそのAPIが無いので
        user_data_dir にフォールバックする。
        """
        if platform == "android":
            try:
                from jnius import autoclass

                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                context = PythonActivity.mActivity
                ext_dir = context.getExternalFilesDir(None)
                if ext_dir is not None:
                    return os.path.join(ext_dir.getAbsolutePath(), "recap_exports")
            except Exception:
                pass

        return os.path.join(App.get_running_app().user_data_dir, "recap_exports")

    def save_image(self):
        """カード部分だけを画像として書き出し、可能ならギャラリーに認識させる"""
        if not self.card:
            return

        out_dir = self._export_dir()
        os.makedirs(out_dir, exist_ok=True)
        filename = os.path.join(out_dir, "habitgraph_weekly_recap.png")

        # 描画が完了してから書き出すため、1フレーム遅らせる
        def do_export(*_):
            self.card.export_to_png(filename)
            self._notify_gallery(filename)
            self.save_status = f"保存しました: {filename}"

        Clock.schedule_once(do_export, 0.05)

    @staticmethod
    def _notify_gallery(filename: str) -> None:
        """Androidのメディアスキャナーに知らせて、ギャラリーにも表示されやすくする。
        失敗しても保存自体は成功しているので、例外は握りつぶして良い。"""
        if platform != "android":
            return
        try:
            from jnius import autoclass

            MediaScannerConnection = autoclass("android.media.MediaScannerConnection")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            MediaScannerConnection.scanFile(
                PythonActivity.mActivity, [filename], None, None
            )
        except Exception:
            pass

    def go_home(self):
        self.manager.transition.direction = "right"
        self.manager.current = "home"
