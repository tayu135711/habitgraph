"""
habitgraph.widgets.bar_chart
------------------------------
外部グラフライブラリ(matplotlib等)を使わず、Kivyのcanvas命令だけで
直近7日間の達成/未達成を棒グラフとして描画するウィジェット。

モバイル配布時にネイティブ依存を増やしたくない(APKサイズ/ビルド安定性)
という理由から、あえて自前描画にしている。
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import ListProperty, ColorProperty
from kivy.metrics import dp


class BarChart(Widget):
    # [(label, done_bool), ...]
    data = ListProperty([])
    bar_color = ColorProperty([0.31, 0.56, 0.97, 1])
    empty_color = ColorProperty([0.2, 0.22, 0.28, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, data=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        if not self.data:
            return

        n = len(self.data)
        gap = dp(8)
        total_gap = gap * (n + 1)
        bar_w = max((self.width - total_gap) / n, 4)
        max_h = self.height * 0.72
        min_h = self.height * 0.10
        label_h = self.height * 0.18

        with self.canvas:
            x = self.x + gap
            for label, done in self.data:
                bar_h = max_h if done else min_h
                Color(*(self.bar_color if done else self.empty_color))
                RoundedRectangle(
                    pos=(x, self.y + label_h),
                    size=(bar_w, bar_h),
                    radius=[bar_w / 2],
                )
                x += bar_w + gap
