from manim import *
from common import *

CLIP = 24.90


class Scene03(Scene):
    def construct(self):
        title = scene_title("Predict first: the budget ledger")
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # Build equation term by term (Text, not MathTex)
        t_eq = Text("t", font_size=44, color=FG)
        eq = Text("=", font_size=44, color=MUTED)
        term1 = Text("FLOP / R", font_size=40, color=GREEN)
        plus1 = Text("+", font_size=40, color=MUTED)
        term2 = Text("bytes / B", font_size=40, color=TEAL)
        plus2 = Text("+", font_size=40, color=MUTED)
        term3 = Text("CPU", font_size=40, color=BLUE)
        row = VGroup(t_eq, eq, term1, plus1, term2, plus2, term3).arrange(RIGHT, buff=0.28)
        row.move_to(UP * 1.6)

        self.play(Write(VGroup(t_eq, eq)), run_time=0.6)
        self.play(FadeIn(term1, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(plus1), FadeIn(term2, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(plus2), FadeIn(term3, shift=UP * 0.2), run_time=0.7)

        cap = VGroup(
            Text("arithmetic / compute rate", font_size=16, color=GREEN),
            Text("bytes / bandwidth", font_size=16, color=TEAL),
            Text("+ CPU overhead", font_size=16, color=BLUE),
        ).arrange(RIGHT, buff=0.7)
        cap.next_to(row, DOWN, buff=0.35)
        self.play(FadeIn(cap), run_time=0.6)

        # Van + traffic lights metaphor
        road = Line(LEFT * 5.5, RIGHT * 5.5, color=MUTED).move_to(DOWN * 1.9)
        self.play(Create(road), run_time=0.5)

        lights = VGroup()
        for i, x in enumerate([-3.5, -1.2, 1.1, 3.4]):
            post = Line(DOWN * 1.9, DOWN * 1.1, color=MUTED).shift(RIGHT * x)
            dot = Dot(point=DOWN * 1.1 + RIGHT * x, radius=0.1, color=ROSE)
            lights.add(VGroup(post, dot))
        self.play(*[Create(l) for l in lights], run_time=0.6)

        van = RoundedRectangle(width=0.9, height=0.5, corner_radius=0.08,
                               stroke_color=SKY, fill_color=SKY, fill_opacity=0.3)
        van.move_to(DOWN * 1.65 + LEFT * 4.6)
        van_lab = Text("small model", font_size=15, color=SKY).move_to(van.get_center() + UP * 0.9)
        self.play(FadeIn(van), FadeIn(van_lab), run_time=0.5)

        # van stutters between lights (lots of waiting)
        for x in [-3.5, -1.2, 1.1, 3.4]:
            self.play(van.animate.move_to(DOWN * 1.65 + RIGHT * x),
                      van_lab.animate.move_to(DOWN * 1.65 + RIGHT * x + UP * 0.9),
                      run_time=0.5)
            self.wait(0.45)  # stuck at the light = launch overhead

        lb = Text("launch-bound: time spent between kernels", font_size=20, color=ROSE)
        lb.move_to(DOWN * 3.0)
        self.play(FadeIn(lb), run_time=0.6)

        tag = source_tag("ledger · note C1")
        self.play(FadeIn(tag), run_time=0.3)
        hold(self, CLIP)
