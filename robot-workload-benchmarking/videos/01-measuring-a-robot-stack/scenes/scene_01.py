from manim import *
from common import *

CLIP = 19.43


class Scene01(Scene):
    def construct(self):
        title = scene_title("One computer, a crowd of services")
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # The computer slab
        slab = RoundedRectangle(width=10.2, height=4.2, corner_radius=0.15,
                                stroke_color=MUTED, stroke_width=2, fill_opacity=0)
        slab.move_to(UP * 0.35)
        self.play(Create(slab), run_time=0.8)

        lanes = [
            ("camera depth   30 Hz", TEAL),
            ("people perception   10 Hz", SKY),
            ("mapping", AMBER),
            ("voice", VIOLET),
            ("control   50 Hz · 20 ms   isolated cores", RED),
        ]
        lane_mobs = VGroup()
        y0 = 1.75
        for i, (label, color) in enumerate(lanes):
            bar = RoundedRectangle(width=9.0, height=0.52, corner_radius=0.1,
                                   stroke_color=color, stroke_width=2,
                                   fill_color=color, fill_opacity=0.18)
            bar.move_to(UP * (y0 - i * 0.72) + LEFT * 0.3)
            txt = Text(label, font_size=19, color=color)
            txt.move_to(bar.get_center())
            lane_mobs.add(VGroup(bar, txt))

        for lm in lane_mobs:
            self.play(FadeIn(lm[0], shift=RIGHT * 0.2), Write(lm[1]), run_time=0.75)

        # shared CPU + GPU chips under lanes
        cpu = RoundedRectangle(width=2.0, height=0.7, corner_radius=0.08,
                               stroke_color=BLUE, fill_color=BLUE, fill_opacity=0.25)
        cpu_t = Text("CPU", font_size=20, color=BLUE)
        gpu = RoundedRectangle(width=2.0, height=0.7, corner_radius=0.08,
                               stroke_color=GREEN, fill_color=GREEN, fill_opacity=0.25)
        gpu_t = Text("GPU", font_size=20, color=GREEN)
        chips = VGroup(VGroup(cpu, cpu_t), VGroup(gpu, gpu_t)).arrange(RIGHT, buff=0.6)
        for c in chips:
            c[1].move_to(c[0].get_center())
        chips.move_to(DOWN * 2.65)
        shared = Text("shared by every service", font_size=16, color=MUTED)
        shared.next_to(chips, DOWN, buff=0.15)
        self.play(FadeIn(chips, shift=UP * 0.2), FadeIn(shared), run_time=0.9)

        tag = source_tag("rates illustrative · constants.json")
        self.play(FadeIn(tag), run_time=0.4)
        hold(self, CLIP)
