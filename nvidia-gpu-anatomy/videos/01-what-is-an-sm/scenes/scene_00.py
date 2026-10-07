"""Scene 00 — title card (static, ~4 s). No narration."""
from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import BG, SOFTWARE, HARDWARE, INK, MUTE


class Scene00(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("From a thread to the chip", font_size=46, color=INK)
        sub = Text("how work lands on an NVIDIA GPU", font_size=28, color=SOFTWARE)
        foot = Text("a concept primer - Orin & Thor", font_size=20, color=MUTE)
        g = VGroup(title, sub, foot).arrange(DOWN, buff=0.4)
        underline = Line(1.6 * LEFT, 1.6 * RIGHT, color=HARDWARE, stroke_width=3)
        underline.next_to(sub, DOWN, buff=0.15)
        self.play(FadeIn(title, shift=0.3 * DOWN), run_time=1.0)
        self.play(FadeIn(sub), Create(underline), run_time=0.8)
        self.play(FadeIn(foot), run_time=0.6)
        self.wait(1.8)
