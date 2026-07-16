"""
habitgraph.widgets.growth_tree
---------------------------------
合計達成回数(HabitStore.total_completions)に応じて育つ「木」を
Kivyのcanvas命令だけで描画するウィジェット。

外部の画像アセットやアニメーションライブラリを使わず、段階(stage)ごとに
枝の本数・葉の量・花の有無を変えることで「育っている感」を出す。
"""
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.properties import NumericProperty, ColorProperty
from kivy.metrics import dp
import math
import random


class GrowthTree(Widget):
    # 0=種 / 1=芽 / 2=若木 / 3=木 / 4=大木 / 5=満開の木
    stage = NumericProperty(0)
    trunk_color = ColorProperty([0.55, 0.4, 0.28, 1])
    leaf_color = ColorProperty([0.30, 0.72, 0.42, 1])
    flower_color = ColorProperty([0.96, 0.55, 0.70, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 見た目のランダム要素(枝の角度や花の位置)を、再描画のたびに
        # 変わらないよう毎回同じシードで固定しておく
        self._rng = random.Random(42)
        self.bind(pos=self._redraw, size=self._redraw, stage=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return

        stage = max(0, min(5, int(self.stage)))
        cx = self.center_x
        ground_y = self.y + self.height * 0.08
        max_h = self.height * 0.8

        with self.canvas:
            # 地面のライン
            Color(1, 1, 1, 0.12)
            Line(points=[self.x + self.width * 0.1, ground_y,
                         self.x + self.width * 0.9, ground_y], width=dp(1.5))

            if stage == 0:
                self._draw_seed(cx, ground_y)
                return

            trunk_h = max_h * (0.25 + 0.15 * stage)
            trunk_top = ground_y + trunk_h
            trunk_w = dp(4) + dp(1.5) * stage

            Color(*self.trunk_color)
            Line(points=[cx, ground_y, cx, trunk_top], width=trunk_w, cap="round")

            if stage == 1:
                # 芽: 葉が2枚だけ
                self._leaf_cluster(cx, trunk_top, radius=dp(10))
                return

            # 段階が進むほど枝分かれと葉のクラスタが増える
            n_branches = stage  # 2〜5本
            leaf_radius = dp(14) + dp(4) * stage

            self._rng.seed(42)
            for i in range(n_branches):
                t = (i + 1) / (n_branches + 1)
                branch_y = ground_y + trunk_h * (0.45 + 0.5 * t)
                angle = math.radians(-55 + 110 * t + self._rng.uniform(-8, 8))
                length = trunk_h * (0.28 + 0.10 * self._rng.random())
                bx = cx + math.sin(angle) * length
                by = branch_y + math.cos(angle) * length * 0.5

                Color(*self.trunk_color)
                Line(points=[cx, branch_y, bx, by], width=dp(2.5), cap="round")
                self._leaf_cluster(bx, by, radius=leaf_radius * (0.7 + 0.3 * self._rng.random()))

            # てっぺんの大きな葉のかたまり
            self._leaf_cluster(cx, trunk_top, radius=leaf_radius * 1.1)

            if stage >= 5:
                self._scatter_flowers(cx, trunk_top, spread=leaf_radius * 1.6, count=7)

    def _draw_seed(self, cx, ground_y):
        Color(*self.trunk_color)
        r = dp(6)
        Ellipse(pos=(cx - r, ground_y - r * 0.6), size=(r * 2, r * 1.2))

    def _leaf_cluster(self, x, y, radius):
        Color(*self.leaf_color)
        Ellipse(pos=(x - radius, y - radius * 0.85), size=(radius * 2, radius * 1.7))

    def _scatter_flowers(self, cx, top_y, spread, count):
        Color(*self.flower_color)
        for i in range(count):
            angle = (2 * math.pi / count) * i
            fx = cx + math.cos(angle) * spread * self._rng.uniform(0.3, 0.9)
            fy = top_y + math.sin(angle) * spread * 0.5 * self._rng.uniform(0.3, 0.9)
            r = dp(3)
            Ellipse(pos=(fx - r, fy - r), size=(r * 2, r * 2))
