"""Scene 06 — The wall: the 172 GB/s floor. Narration ~31.40 s."""
from manim import *
from theme import (BG, CONTROL, MEMORY, DANGER, GHOST, INK,
                   FLOOR, DRAM_SUSTAINED_THOR, src_tag)

CLIP = 31.40


class Scene06(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("The wall: the shared-controller floor", font_size=34, color=INK).to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # redraw the ladder's good steps small
        labels = ["separate\nprocess", "MPS", "MPS +\n25% cap"]
        cols = [MEMORY, GHOST, CONTROL]
        boxes = VGroup()
        x = -4.0
        for lab, col in zip(labels, cols):
            b = Rectangle(width=2.0, height=1.3, stroke_color=col, fill_color=col, fill_opacity=0.25, stroke_width=3)
            b.move_to([x, 1.3, 0])
            t = Text(lab, font_size=16, color=INK).move_to(b.get_center())
            boxes.add(VGroup(b, t))
            x += 2.8
        self.play(LaggedStart(*[FadeIn(g) for g in boxes], lag_ratio=0.3), run_time=1.4)

        # the floor sweeps in
        floor = Line([-6.2, -0.3, 0], [6.2, -0.3, 0], color=DANGER, stroke_width=6)
        floor_lab = Text(f"~{FLOOR:g} GB/s  CPU memory load", font_size=22, color=DANGER)
        floor_lab.next_to(floor, UP, buff=0.12).align_to(floor, LEFT).shift(RIGHT * 0.3)
        self.play(Create(floor), run_time=1.2)
        self.play(FadeIn(floor_lab), run_time=0.8)

        # roof context: 245 GB/s sustained, 172 = ~70%
        roof = Text(f"{DRAM_SUSTAINED_THOR:g} GB/s sustained roof", font_size=17, color=GHOST)
        roof.to_edge(RIGHT, buff=0.4).shift(UP * 2.6)
        pct = Text(f"~{FLOOR:g} = 70% of it", font_size=17, color=DANGER)
        pct.next_to(roof, DOWN, buff=0.12).align_to(roof, RIGHT)
        self.play(FadeIn(roof), FadeIn(pct), run_time=1.0)

        # every step collapses to red below the floor
        reds = VGroup()
        for g in boxes:
            r = Rectangle(width=2.0, height=1.3, stroke_color=DANGER,
                          fill_color=DANGER, fill_opacity=0.3, stroke_width=3)
            r.move_to([g[0].get_center()[0], -1.5, 0])
            reds.add(r)
        self.play(
            *[g.animate.set_opacity(0.25) for g in boxes],
            LaggedStart(*[FadeIn(r, shift=DOWN * 0.4) for r in reds], lag_ratio=0.2),
            run_time=1.6,
        )

        verdict = Text("every discipline collapses", font_size=20, color=DANGER)
        verdict.next_to(reds, DOWN, buff=0.25)
        punch = Text("Scheduling cannot fix a memory problem", font_size=28, color=INK)
        punch.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(verdict), run_time=0.8)
        self.play(Write(punch), run_time=1.4)

        tag = src_tag("params: cpu_memory_load_floor, dram_bandwidth_sustained_M  (L4)").to_corner(DR, buff=0.12)
        self.play(FadeIn(tag), run_time=0.5)

        used = 1.0 + 1.4 + 1.2 + 0.8 + 1.0 + 1.4 + 0.8 + 1.4 + 0.5
        self.wait(max(0.5, CLIP + 0.5 - used))
