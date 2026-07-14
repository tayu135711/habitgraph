"""
habitgraph.widgets.habit_card
--------------------------------
ホーム画面のリストに並ぶ、習慣1件分の行ウィジェット。
見た目(色・レイアウト)は habitgraph.kv 側の `<HabitCard>` ルールで定義し、
ここではロジック(タップ時のトグル呼び出し)だけを持つ。
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ObjectProperty


class HabitCard(BoxLayout):
    habit_id = StringProperty("")
    habit_name = StringProperty("")
    habit_color = StringProperty("#4F8EF7")
    streak = NumericProperty(0)
    done_today = BooleanProperty(False)

    # HomeScreen から渡されるコールバック: on_toggle(habit_id)
    on_toggle = ObjectProperty(None, allownone=True)

    def toggle(self):
        if self.on_toggle:
            self.on_toggle(self.habit_id)
