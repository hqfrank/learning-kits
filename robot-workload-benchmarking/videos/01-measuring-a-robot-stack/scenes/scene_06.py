from manim import *
from common import *

CLIP = 23.93


class Scene06(Scene):
    def construct(self):
        title = scene_title("How the bench can lie", color=ROSE)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        cards_data = [
            ("Shared link slows\nthe control bus", "434 Hz vs 500 Hz target",
             "isolate the control link"),
            ("Interrupts pile\non core 0", "default routing",
             "move IRQ to a free core"),
            ("Tracing perturbs", "adds ~15 ms latency",
             "trace-only windows"),
            ("All-zero data\noverstates speed", "datapath never toggles",
             "use random operands"),
        ]
        cards = VGroup()
        for head, num, rule in cards_data:
            box = RoundedRectangle(width=3.0, height=2.5, corner_radius=0.12,
                                   stroke_color=ROSE, stroke_width=2, fill_opacity=0.06,
                                   fill_color=ROSE)
            h = Text(head, font_size=18, color=FG, line_spacing=0.8).move_to(
                box.get_top() + DOWN * 0.55)
            n = Text(num, font_size=15, color=ROSE).move_to(box.get_center() + DOWN * 0.05)
            r = Text("→ " + rule, font_size=14, color=GREEN).move_to(
                box.get_bottom() + UP * 0.4)
            cards.add(VGroup(box, h, n, r))
        cards.arrange(RIGHT, buff=0.35).move_to(DOWN * 0.3)

        for c in cards:
            self.play(FadeIn(c, shift=UP * 0.2), run_time=0.7)

        note = Text("a clean number can still be wrong", font_size=20, color=ROSE)
        note.to_edge(DOWN, buff=0.4)
        self.play(FadeIn(note), run_time=0.6)

        tag = source_tag("434/500 Hz & 15 ms illustrative · C7 / constants.json")
        self.play(FadeIn(tag), run_time=0.3)
        hold(self, CLIP)
