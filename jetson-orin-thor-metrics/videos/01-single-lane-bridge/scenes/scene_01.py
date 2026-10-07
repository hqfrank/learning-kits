"""Scene 01 — Three jobs, one GPU. Narration ~24.8 s."""
from manim import *
from theme import (BG, CONTROL, MEMORY, VLA, INK, GHOST, src_tag)

CLIP = 24.78  # measured ffprobe duration of audio/scene_01.wav


class Scene01(Scene):
    def construct(self):
        self.camera.background_color = BG

        title = Text("Three jobs, one GPU", font_size=40, color=INK).to_edge(UP, buff=0.5)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # The three jobs
        def job(label, sub, color):
            box = RoundedRectangle(width=3.0, height=1.1, corner_radius=0.12,
                                   stroke_color=color, fill_color=color, fill_opacity=0.18)
            t1 = Text(label, font_size=24, color=color)
            t2 = Text(sub, font_size=16, color=INK)
            grp = VGroup(t1, t2).arrange(DOWN, buff=0.12)
            return VGroup(box, grp)

        control = job("CONTROL (WBC)", "100 Hz  ·  10 ms deadline", CONTROL)
        percep = job("PERCEPTION", "cameras", MEMORY)
        planner = job("VLA  (pi0.5)", "plans ~5 Hz", VLA)
        jobs = VGroup(control, percep, planner).arrange(RIGHT, buff=0.5)
        jobs.next_to(title, DOWN, buff=0.7)

        # Shared SoC stack
        gpu = RoundedRectangle(width=4.2, height=0.8, corner_radius=0.1,
                               stroke_color=INK, fill_color=GHOST, fill_opacity=0.12)
        gpu_t = Text("one GPU", font_size=20, color=INK)
        gpu_grp = VGroup(gpu, gpu_t)
        mc = RoundedRectangle(width=4.2, height=0.7, corner_radius=0.1,
                              stroke_color=MEMORY, fill_color=MEMORY, fill_opacity=0.2)
        mc_t = Text("one memory controller", font_size=18, color=INK)
        mc_grp = VGroup(mc, mc_t)
        pool = RoundedRectangle(width=4.2, height=0.7, corner_radius=0.1,
                                stroke_color=MEMORY, fill_color=MEMORY, fill_opacity=0.12)
        pool_t = Text("one LPDDR pool", font_size=18, color=INK)
        pool_grp = VGroup(pool, pool_t)
        stack = VGroup(gpu_grp, mc_grp, pool_grp).arrange(DOWN, buff=0.25)
        stack.next_to(jobs, DOWN, buff=0.9)

        # drop the three jobs in one at a time
        self.play(FadeIn(control, shift=DOWN * 0.3), run_time=1.2)
        self.play(FadeIn(percep, shift=DOWN * 0.3), run_time=1.0)
        self.play(FadeIn(planner, shift=DOWN * 0.3), run_time=1.0)

        self.play(FadeIn(gpu_grp), run_time=0.8)
        # funnel arrows from all three jobs into the single GPU
        arrows = VGroup(*[
            Arrow(j[0].get_bottom(), gpu.get_top(), buff=0.1,
                  stroke_width=3, color=c, max_tip_length_to_length_ratio=0.08)
            for j, c in [(control, CONTROL), (percep, MEMORY), (planner, VLA)]
        ])
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.3), run_time=1.6)
        self.play(FadeIn(mc_grp), FadeIn(pool_grp), run_time=1.0)
        a2 = Arrow(gpu.get_bottom(), mc.get_top(), buff=0.1, stroke_width=3, color=INK)
        a3 = Arrow(mc.get_bottom(), pool.get_top(), buff=0.1, stroke_width=3, color=INK)
        self.play(GrowArrow(a2), GrowArrow(a3), run_time=1.0)

        bridge = Text("a single-lane bridge", font_size=26, color=CONTROL)
        bridge.next_to(stack, DOWN, buff=0.4)
        self.play(Write(bridge), run_time=1.2)

        tag = src_tag("params: wbc_deadline, mps_cap_vla_rate_retained").to_corner(DR, buff=0.2)
        self.play(FadeIn(tag), run_time=0.6)

        # hold to fill the clip
        used = 1.0 + 1.2 + 1.0 + 1.0 + 0.8 + 1.6 + 1.0 + 1.0 + 1.2 + 0.6
        self.wait(max(0.5, CLIP + 0.5 - used))
