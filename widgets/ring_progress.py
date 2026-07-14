"""
habitgraph.widgets.ring_progress
-----------------------------------
「今日の達成率」を円形リングで表示するウィジェット。
kivy.graphics.Line(circle=...) の角度指定機能を使い、
背景の薄いリングの上に達成率ぶんだけ濃い色のアークを重ねて描く。
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line
from kivy.properties import NumericProperty, ColorProperty
from kivy.metrics import dp


class RingProgress(Widget):
    # 0.0 - 1.0
    progress = NumericProperty(0.0)
    ring_color = ColorProperty([0.31, 0.56, 0.97, 1])
    track_color = ColorProperty([0.2, 0.22, 0.28, 1])
    thickness = NumericProperty(dp(10))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, progress=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        size = min(self.width, self.height)
        if size <= 0:
            return
        cx = self.center_x
        cy = self.center_y
        radius = (size / 2) - self.thickness

        with self.canvas:
            # background track
            Color(*self.track_color)
            Line(
                circle=(cx, cy, radius, 0, 360),
                width=self.thickness,
                cap="round",
            )
            # progress arc (12時方向スタートで時計回り)
            Color(*self.ring_color)
            sweep = max(0.0, min(1.0, self.progress)) * 360
            if sweep > 0:
                Line(
                    circle=(cx, cy, radius, 90 - sweep, 90),
                    width=self.thickness,
                    cap="round",
                )
