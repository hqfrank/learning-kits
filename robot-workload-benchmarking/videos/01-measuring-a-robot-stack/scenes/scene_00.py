from manim import *
from common import *


class Scene00(Scene):
    def construct(self):
        t1 = Text("Measuring a robot's brain", font_size=52, color=FG, weight=BOLD)
        t2 = Text("without fooling yourself", font_size=40, color=TEAL)
        VGroup(t1, t2).arrange(DOWN, buff=0.4)
        self.play(FadeIn(t1, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(t2, shift=UP * 0.2), run_time=0.6)
        self.wait(1.4)
