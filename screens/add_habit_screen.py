"""
habitgraph.screens.add_habit_screen
--------------------------------------
新しい習慣を登録する画面。名前の入力と、あらかじめ用意した
カラーパレットからのアクセントカラー選択のみのシンプルなフォーム。
"""
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App

PALETTE = [
    "#4F8EF7",  # blue
    "#22C55E",  # green
    "#F97316",  # orange
    "#EF4444",  # red
    "#A855F7",  # purple
    "#EAB308",  # yellow
]


class AddHabitScreen(Screen):
    name_input = ObjectProperty(None)
    palette_grid = ObjectProperty(None)
    selected_color = StringProperty(PALETTE[0])

    def on_pre_enter(self, *args):
        self.name_input.text = ""
        self.selected_color = PALETTE[0]
        # ToggleButton(カラースウォッチ)は状態(state)を自分で保持しているため、
        # selected_color をデフォルトに戻すだけでは見た目が前回選択のまま残ってしまう。
        # ここで明示的に「デフォルト色だけdown、他はnormal」に揃える。
        if self.palette_grid:
            for swatch in self.palette_grid.children:
                swatch.state = "down" if swatch.swatch_hex == PALETTE[0] else "normal"

    def pick_color(self, color: str):
        self.selected_color = color

    def save(self):
        name = (self.name_input.text or "").strip()
        if not name:
            return  # 空欄では保存しない(kv側でボタンをdisabledにしても良い)

        store = App.get_running_app().store
        store.add_habit(name, self.selected_color)

        self.manager.transition.direction = "right"
        self.manager.current = "home"

    def cancel(self):
        self.manager.transition.direction = "right"
        self.manager.current = "home"
