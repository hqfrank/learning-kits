from manim import *
from common import *

CLIP = 17.35


class Scene02(Scene):
    def construct(self):
        title = scene_title("Does it fit? What runs out first?")
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        q1 = Text("Does it all fit?", font_size=40, color=FG)
        q1.move_to(UP * 1.2)
        self.play(Write(q1), run_time=1.0)
        self.wait(0.4)

        q2 = Text("What runs out first?", font_size=40, color=ORANGE)
        q2.move_to(UP * 1.2)
        self.play(ReplacementTransform(q1, q2), run_time=1.0)

        # three resource bars, unfilled
        labels = [("CPU", BLUE), ("GPU", GREEN), ("memory", TEAL)]
        bars = VGroup()
        for name, color in labels:
            frame = RoundedRectangle(width=1.4, height=2.6, corner_radius=0.08,
                                     stroke_color=color, stroke_width=2, fill_opacity=0)
            lab = Text(name, font_size=22, color=color)
            lab.next_to(frame, DOWN, buff=0.2)
            bars.add(VGroup(frame, lab))
        bars.arrange(RIGHT, buff=1.1).move_to(DOWN * 1.4)
        self.play(*[Create(b[0]) for b in bars], *[Write(b[1]) for b in bars], run_time=1.2)

        caveat = Text("one average number cannot answer this", font_size=20, color=MUTED)
        caveat.next_to(bars, DOWN, buff=0.5)
        self.play(FadeIn(caveat), run_time=0.6)

        tag = source_tag("method · note A0")
        self.play(FadeIn(tag), run_time=0.4)
        hold(self, CLIP)
