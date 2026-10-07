"""Scene 07 — sources card (static, ~7 s). No narration."""
from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import BG, INK, MUTE


class Scene07(Scene):
    def construct(self):
        self.camera.background_color = BG
        head = Text("Sources", font_size=38, color=INK).to_edge(UP, buff=0.8)

        lines = [
            ("All constants: explorers/params.json", INK),
            ("-> metrics-kit constants.json", MUTE),
            ("-> Jetson Orin/Thor metrics kit (Table 1; A.6; A.7)", MUTE),
            ("CUDA model: CUDA Programming Guide v13.4.2", INK),
            ("sections 1.2 and 3.2.2", MUTE),
            ("\"Same occupancy, 4x runtime\": note 03 (B3)", INK),
        ]
        body = VGroup(*[Text(t, font_size=24, color=c) for t, c in lines])
        body.arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        body.next_to(head, DOWN, buff=0.6)

        self.play(FadeIn(head, shift=0.3 * DOWN), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(l, shift=0.15 * UP) for l in body],
                              lag_ratio=0.25), run_time=2.6)
        self.wait(3.0)
