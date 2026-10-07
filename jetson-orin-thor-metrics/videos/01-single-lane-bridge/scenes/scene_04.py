"""Scene 04 — The real rehearsal: 41.6 us -> 5.9 ms. Narration ~32.18 s."""
from manim import *
from theme import (BG, CONTROL, MEMORY, VLA, DANGER, GHOST, INK,
                   WBC_SOLO_P99_THOR, WBC_WORST_MIX, WBC_DEADLINE, src_tag)

CLIP = 32.18


class Scene04(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("The real rehearsal", font_size=38, color=INK).to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # y axis in ms, 0..11, deadline at 10
        ax = Axes(
            x_range=[0, 5, 1], y_range=[0, 11, 2],
            x_length=8.5, y_length=4.6,
            axis_config={"color": GHOST, "stroke_width": 2, "include_numbers": False},
            y_axis_config={"include_tip": False},
            x_axis_config={"include_tip": False, "include_ticks": False},
        ).shift(DOWN * 0.3 + LEFT * 0.5)
        yticks = VGroup()
        for yv in [0, 2, 4, 6, 8, 10]:
            lbl = Text(f"{yv}", font_size=15, color=GHOST).next_to(ax.c2p(0, yv), LEFT, buff=0.12)
            yticks.add(lbl)
        ylab = Text("WBC p99 (ms)", font_size=18, color=INK).rotate(PI / 2).next_to(yticks, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(yticks), FadeIn(ylab), run_time=1.2)

        # red deadline line at 10 ms
        dline = DashedLine(ax.c2p(0, WBC_DEADLINE), ax.c2p(5, WBC_DEADLINE), color=DANGER, stroke_width=3)
        dlab = Text("10 ms deadline", font_size=18, color=DANGER).next_to(dline, UP, buff=0.08).align_to(dline, RIGHT)
        self.play(Create(dline), FadeIn(dlab), run_time=1.0)

        def bar(xc, val, color, w=0.7):
            h0 = ax.c2p(0, 0)
            top = ax.c2p(0, val)
            height = top[1] - h0[1]
            r = Rectangle(width=w, height=max(height, 0.03), stroke_color=color,
                          fill_color=color, fill_opacity=0.85, stroke_width=2)
            r.move_to([ax.c2p(xc, 0)[0], h0[1] + max(height, 0.03) / 2, 0])
            return r

        # solo: 0.0416 ms -> a sliver
        solo = bar(0.6, WBC_SOLO_P99_THOR, CONTROL)
        solo_lab = Text("41.6 us\nsolo", font_size=15, color=CONTROL).next_to(solo, UP, buff=0.1)
        self.play(GrowFromEdge(solo, DOWN), FadeIn(solo_lab), run_time=1.0)

        # cumulative mix: +perception, +VLA, +CPU hog growing to 5.9 ms
        steps = [(1.8, 1.7, "+ compute\nco-tenant", MEMORY),
                 (3.0, 3.4, "+ CPU hog", VLA),
                 (4.2, WBC_WORST_MIX, "+ full roster\n+ CPU hog", DANGER)]
        prev = None
        for xc, val, lab, col in steps:
            b = bar(xc, val, col)
            t = Text(lab, font_size=14, color=INK).next_to(b, UP, buff=0.08)
            self.play(GrowFromEdge(b, DOWN), FadeIn(t), run_time=1.1)
            prev = b

        # big callout
        callout = VGroup(
            Text("41.6 us  ->  5.9 ms", font_size=30, color=INK),
            Text("141x — most of the budget gone", font_size=22, color=DANGER),
        ).arrange(DOWN, buff=0.15).to_edge(RIGHT, buff=0.4).shift(UP * 0.6)
        self.play(Write(callout[0]), run_time=1.2)
        self.play(FadeIn(callout[1], shift=UP * 0.2), run_time=1.0)

        tag = src_tag("params: wbc_solo_p99, wbc_worst_mix_p99  (B.8)").to_corner(DR, buff=0.15)
        self.play(FadeIn(tag), run_time=0.5)

        used = 1.0 + 1.2 + 1.0 + 1.0 + 3 * 1.1 + 1.2 + 1.0 + 0.5
        self.wait(max(0.5, CLIP + 0.5 - used))
