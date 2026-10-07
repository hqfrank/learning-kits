"""Scene 05 — the memory ladder, Orin -> Thor numbers animate in.
Narration clip = 40.70 s. Scene length target >= 41.20 s.
All numbers from explorers/params.json:
  l1_shared_per_sm 164/228 KB; l2_size 4/32 MB; l2_dram_capacity_ratio 8x;
  latency_l2 146/156 ns; l2_dram_bandwidth_ratio 12.4/14.6x.
"""
from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import BG, ORIN, THOR, LIMIT, SCHED, INK, MUTE, source_tag

CLIP = 40.70


def row(level, orin, thor, color_v=THOR):
    name = Text(level, font_size=22, color=INK)
    box = RoundedRectangle(corner_radius=0.08, width=3.1, height=0.72,
                           stroke_color=MUTE, stroke_width=2, fill_color=MUTE, fill_opacity=0.08)
    name.move_to(box)
    val = Text(f"{orin}  ->  {thor}", font_size=20, color=color_v)
    return VGroup(box, name), val


class Scene05(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("The memory ladder", font_size=30, color=INK).to_edge(UP, buff=0.35)
        self.play(FadeIn(title, shift=0.3 * DOWN), run_time=0.8)
        self.add(source_tag("l1/l2_size/latency_l2/l2_dram_bandwidth_ratio"))

        key = Text("Orin  ->  Thor", font_size=18, color=INK).to_corner(UR, buff=0.4)
        okey = Text("Orin", font_size=16, color=ORIN)
        tkey = Text("Thor", font_size=16, color=THOR)
        VGroup(okey, tkey).arrange(RIGHT, buff=0.3).next_to(key, DOWN, buff=0.1)
        self.add(key, okey, tkey)

        # ladder rows (fastest/smallest at top)
        rows = [
            ("registers", "per thread", "per thread"),
            ("L1 / shared", "164 KB", "228 KB"),
            ("L2 (shared)", "4 MB", "32 MB"),
            ("DRAM", "177 GB/s", "259 GB/s"),
        ]
        boxes = VGroup()
        vals = VGroup()
        for lv, o, t in rows:
            b, v = row(lv, o, t)
            boxes.add(b)
            vals.add(v)
        boxes.arrange(DOWN, buff=0.3).next_to(title, DOWN, buff=0.55).shift(2.6 * LEFT)
        for b, v in zip(boxes, vals):
            v.next_to(b, RIGHT, buff=0.6)

        for i, (b, v) in enumerate(zip(boxes, vals)):
            self.play(FadeIn(b, shift=0.15 * RIGHT), run_time=0.5)
            self.play(FadeIn(v), run_time=0.6)
            if i < len(boxes) - 1:
                pass
        self.wait(1.0)

        # badges: x8 on L2, ~same latency, 12.4x/14.6x bandwidth cliff
        l2box = boxes[2]
        x8 = Text("x8 capacity", font_size=20, color=SCHED)
        x8.next_to(vals[2], RIGHT, buff=0.5)
        self.play(FadeIn(x8, shift=0.2 * RIGHT), run_time=0.8)
        self.wait(1.5)

        lat = Text("L2 latency 146 -> 156 ns  (~same)", font_size=20, color=LIMIT)
        lat.next_to(boxes, DOWN, buff=0.5)
        self.play(Write(lat), run_time=1.5)
        self.wait(2.5)

        cliff = Text("L2 streaming: 12.4x / 14.6x DRAM bandwidth", font_size=20, color=THOR)
        cliff.next_to(lat, DOWN, buff=0.3)
        self.play(Write(cliff), run_time=1.5)
        self.wait(2.0)

        # the 4 MB / 32 MB cliff as a compact step (kept clear of the bottom edge)
        step = VGroup(
            Line(ORIGIN, 0.9 * RIGHT, color=THOR, stroke_width=4),
            Line(0.9 * RIGHT, 0.9 * RIGHT + 0.7 * DOWN, color=LIMIT, stroke_width=4),
            Line(0.9 * RIGHT + 0.7 * DOWN, 1.9 * RIGHT + 0.7 * DOWN, color=LIMIT, stroke_width=4),
        )
        cl = Text("fits L2", font_size=15, color=THOR)
        cr = Text("spills: DRAM tax", font_size=15, color=LIMIT)
        cl.next_to(step[0], UP, buff=0.08)
        cr.next_to(step[2], UP, buff=0.08)
        stepg = VGroup(step, cl, cr)
        stepg.next_to(cliff, DOWN, buff=0.3).shift(0.5 * RIGHT)
        self.play(Create(step), FadeIn(cl), FadeIn(cr), run_time=1.5)

        self.wait(max(0.5, CLIP + 0.6 - self.renderer.time))
