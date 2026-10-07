"""Scene 01 — the software ladder: thread -> warp -> block -> grid -> kernel.
Narration clip audio/scene_01.wav = 23.12 s. Scene length target >= 23.62 s.
"""
from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import BG, SOFTWARE, INK, MUTE, rung, source_tag

CLIP = 23.12


class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = Text("You write a kernel", font_size=34, color=INK).to_edge(UP, buff=0.5)
        self.play(FadeIn(title, shift=0.3 * DOWN), run_time=0.8)

        # software ladder, bottom-up (blue)
        labels = ["thread", "warp = 32 threads", "block", "grid", "kernel"]
        rungs = VGroup(*[rung(l, SOFTWARE) for l in labels])
        rungs.arrange(UP, buff=0.28).next_to(title, DOWN, buff=0.5)

        tag = source_tag("warp=32  CUDA PG 1.2.2.2")
        self.add(tag)

        # pacing: ~4s per rung reveal + connectors, filling the 23s clip
        per = 3.6
        prev = None
        for r in rungs:
            self.play(FadeIn(r, shift=0.3 * UP), run_time=0.9)
            if prev is not None:
                arrow = Arrow(prev.get_top(), r.get_bottom(), buff=0.05,
                              stroke_width=3, color=MUTE, max_tip_length_to_length_ratio=0.15)
                self.play(GrowArrow(arrow), run_time=0.6)
            self.wait(per - 1.5)
            prev = r

        # hold to fill remaining time to clip + 0.5s
        self.wait(max(0.5, CLIP + 0.6 - self.renderer.time))
