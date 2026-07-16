"""
habitgraph.screens.garden_screen
------------------------------------
全習慣を通じた「生涯の合計達成回数」に応じて木が育つ画面。
チェックリストの積み重ねを、数字だけでなく視覚的な"育ち"として見せる。
"""
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.app import App

from data.storage import growth_stage_for, next_growth_threshold

STAGE_LABELS = {
    "seed": "たね",
    "sprout": "芽",
    "sapling": "若木",
    "young_tree": "木",
    "full_tree": "大きな木",
    "blooming_tree": "満開の木",
}


class GardenScreen(Screen):
    tree = ObjectProperty(None)
    total_completions = NumericProperty(0)
    stage_label = StringProperty("たね")
    next_hint = StringProperty("")

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        store = App.get_running_app().store
        total = store.total_completions()
        stage_index, stage_name = growth_stage_for(total)
        remaining = next_growth_threshold(total)

        self.total_completions = total
        self.stage_label = STAGE_LABELS.get(stage_name, stage_name)
        if self.tree:
            self.tree.stage = stage_index

        if remaining is None:
            self.next_hint = "最大まで育ちました"
        else:
            self.next_hint = f"次の段階まであと {remaining} 回"

    def go_home(self):
        self.manager.transition.direction = "right"
        self.manager.current = "home"
