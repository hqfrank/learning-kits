"""Title card (~2.5 s) and Sources card (~6 s). No narration."""
from manim import *
from theme import BG, CONTROL, VLA, GHOST, INK, DANGER, MEMORY


class TitleCard(Scene):
    def construct(self):
        self.camera.background_color = BG
        t = Text("The single-lane bridge", font_size=52, color=CONTROL)
        sub = Text("why a robot's control loop starves on a shared GPU",
                   font_size=26, color=INK)
        tag = Text("Jetson Thor T5000 (sm_110) — measured", font_size=18, color=VLA)
        g = VGroup(t, sub, tag).arrange(DOWN, buff=0.4)
        self.play(FadeIn(t, shift=UP * 0.2), run_time=0.9)
        self.play(FadeIn(sub), FadeIn(tag), run_time=0.8)
        self.wait(1.3)


class SourcesCard(Scene):
    def construct(self):
        self.camera.background_color = BG
        head = Text("Sources", font_size=40, color=INK).to_edge(UP, buff=0.8)
        body = VGroup(
            Text("All numbers from book.pdf (Docs A, B) + L4 KEY-LEARNINGS,", font_size=22, color=INK),
            Text("loaded via explorers/params.json.", font_size=22, color=INK),
        ).arrange(DOWN, buff=0.1).next_to(head, DOWN, buff=0.5)
        items = VGroup(
            Text("A.3 / A.4  tensor & NVFP4 ceilings", font_size=20, color=VLA),
            Text("B.4  SM co-scheduling lockout (8% Orin / 14% Thor)", font_size=20, color=CONTROL),
            Text("B.8  WBC mix ladder (41.6 us -> 5.9 ms, 141x)", font_size=20, color=MEMORY),
            Text("L4  scheduling ladder & ~172 GB/s floor", font_size=20, color=DANGER),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).next_to(body, DOWN, buff=0.5)
        foot = Text("Jetson Thor T5000, MAXN, clocks locked.  A study aid — rough edges expected.",
                    font_size=16, color=GHOST).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(head), run_time=0.6)
        self.play(FadeIn(body), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(i, shift=RIGHT * 0.2) for i in items], lag_ratio=0.3), run_time=2.0)
        self.play(FadeIn(foot), run_time=0.6)
        self.wait(1.6)
