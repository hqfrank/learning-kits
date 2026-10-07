"""Scene 03 — zoom into one SM: four sub-partitions; 512-thread block -> 16 warps -> 4 per SMSP.
Narration clip = 33.08 s. Scene length target >= 33.58 s.
Numbers: smsp_per_sm 4, dispatch_bound_per_smsp 1, fp32_cores_per_sm 128.
"""
from manim import *
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from theme import BG, SOFTWARE, HARDWARE, SCHED, TENSOR, INK, MUTE, source_tag

CLIP = 33.08


class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("Inside one SM: four sub-partitions", font_size=30, color=INK).to_edge(UP, buff=0.35)
        self.play(FadeIn(title, shift=0.3 * DOWN), run_time=0.8)
        self.add(source_tag("smsp 4 - dispatch 1/cyc - fp32 128"))

        # four sub-partition columns
        cols = VGroup()
        for i in range(4):
            header = RoundedRectangle(corner_radius=0.06, width=1.5, height=0.5,
                                      stroke_color=SCHED, stroke_width=3,
                                      fill_color=SCHED, fill_opacity=0.2)
            htxt = Text("1 inst/cyc", font_size=16, color=INK).move_to(header)
            body = RoundedRectangle(corner_radius=0.06, width=1.5, height=1.9,
                                    stroke_color=HARDWARE, stroke_width=2,
                                    fill_color=HARDWARE, fill_opacity=0.07)
            col = VGroup(body, header, VGroup(htxt))
            header.next_to(body, UP, buff=0.08)
            htxt.move_to(header)
            cols.add(col)
        cols.arrange(RIGHT, buff=0.35).next_to(title, DOWN, buff=0.5)

        self.play(LaggedStart(*[FadeIn(c, shift=0.2 * UP) for c in cols], lag_ratio=0.2), run_time=2.2)

        # detail inside column 0: FP32 lanes, INT, LD/ST, tensor core
        body0 = cols[0][0]
        lanes = Text("32 FP32 lanes", font_size=14, color=SOFTWARE)
        intp = Text("INT", font_size=14, color=INK)
        ldst = Text("LD/ST", font_size=14, color=INK)
        tc = Text("tensor core", font_size=14, color=TENSOR)
        detail = VGroup(lanes, intp, ldst, tc).arrange(DOWN, buff=0.12).move_to(body0)
        self.play(FadeIn(detail), run_time=1.2)
        self.wait(1.0)

        # issue ceiling callout (orange)
        callout = Text("4 x 1 = 4 inst / cycle", font_size=24, color=SCHED)
        callout.next_to(cols, DOWN, buff=0.4)
        self.play(Write(callout), run_time=1.2)
        self.wait(2.0)

        # clear the detail labels so landing warps do not overprint them
        self.play(FadeOut(detail), run_time=0.6)

        # 512-thread block -> 16 warps -> 4 per sub-partition
        block = RoundedRectangle(corner_radius=0.1, width=3.2, height=0.7,
                                 stroke_color=SOFTWARE, stroke_width=3,
                                 fill_color=SOFTWARE, fill_opacity=0.16)
        btxt = Text("512-thread block = 16 warps", font_size=20, color=INK).move_to(block)
        blockg = VGroup(block, btxt).next_to(callout, DOWN, buff=0.4)
        self.play(FadeIn(blockg, shift=0.2 * UP), run_time=1.2)
        self.wait(1.5)

        # make 16 warp chips, fly 4 into each column
        warps = VGroup(*[
            RoundedRectangle(corner_radius=0.05, width=0.42, height=0.2,
                             stroke_color=SOFTWARE, stroke_width=1.5,
                             fill_color=SOFTWARE, fill_opacity=0.5)
            for _ in range(16)
        ])
        warps.arrange_in_grid(rows=2, cols=8, buff=0.07).move_to(block.get_center())
        self.play(ReplacementTransform(blockg, VGroup(warps, btxt.copy().set_opacity(0))), run_time=1.0)

        anims = []
        for i in range(4):
            targets = VGroup(*warps[i * 4:(i + 1) * 4]).copy()
            targets.arrange(DOWN, buff=0.08).move_to(cols[i][0].get_center() + 0.0 * DOWN)
            for k in range(4):
                anims.append(warps[i * 4 + k].animate.move_to(targets[k].get_center()).scale(0.9))
        self.play(LaggedStart(*anims, lag_ratio=0.05), run_time=3.0)

        land = Text("4 warps per sub-partition", font_size=18, color=INK).to_edge(DOWN, buff=0.6)
        self.play(FadeIn(land), run_time=0.8)

        self.wait(max(0.5, CLIP + 0.6 - self.renderer.time))
