"""Scene 03 — The cliff: SM co-scheduling lockout. Narration ~37.85 s."""
from manim import *
from theme import (BG, CONTROL, VLA, GHOST, INK, DANGER,
                   LOCKOUT_THOR, LOCKOUT_ORIN, src_tag)

CLIP = 37.85


class Scene03(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("The cliff: SM co-scheduling lockout", font_size=36, color=INK).to_edge(UP, buff=0.4)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        ax = Axes(
            x_range=[0, 30, 5], y_range=[0, 1.1, 0.5],
            x_length=9.5, y_length=4.2,
            axis_config={"color": GHOST, "stroke_width": 2, "include_tip": True,
                         "include_numbers": False},
        ).shift(DOWN * 0.4)
        # manual x tick labels (Text, no LaTeX)
        xticks = VGroup()
        for xv in [0, 8, 14, 20, 30]:
            lbl = Text(f"{xv}", font_size=16, color=GHOST).next_to(ax.c2p(xv, 0), DOWN, buff=0.12)
            xticks.add(lbl)
        xlab = Text("GPU co-tenant occupancy  (% warp slots)", font_size=18, color=INK)
        xlab.next_to(ax.x_axis, DOWN, buff=0.55)
        ylab = Text("victim's first\ncompletion", font_size=16, color=INK)
        ylab.next_to(ax.y_axis, LEFT, buff=0.2)
        self.play(Create(ax), FadeIn(xticks), FadeIn(xlab), FadeIn(ylab), run_time=1.5)

        # ghost: what proportional (fair) sharing would look like — gentle slope, crossed out
        fair = ax.plot(lambda x: 0.05 + 0.010 * x, x_range=[0, 30], color=GHOST, stroke_width=3)
        fair = DashedVMobject(fair, num_dashes=30)
        fair_lab = Text("if sharing were fair", font_size=15, color=GHOST)
        fair_lab.move_to(ax.c2p(23, 0.42))
        self.play(Create(fair), FadeIn(fair_lab), run_time=1.2)
        cross = Line(ax.c2p(16, 0.55), ax.c2p(29, 0.18), color=DANGER, stroke_width=4)
        self.play(Create(cross), run_time=0.6)

        # Thor: flat near zero up to 14%, then SNAP to plateau (= co-tenant lifetime)
        t_flat = Line(ax.c2p(0, 0.05), ax.c2p(LOCKOUT_THOR, 0.05), color=CONTROL, stroke_width=5)
        t_snap = Line(ax.c2p(LOCKOUT_THOR, 0.05), ax.c2p(LOCKOUT_THOR, 1.0), color=VLA, stroke_width=5)
        t_plat = Line(ax.c2p(LOCKOUT_THOR, 1.0), ax.c2p(30, 1.0), color=VLA, stroke_width=5)
        self.play(Create(t_flat), run_time=1.0)
        self.play(Create(t_snap), run_time=0.8)
        self.play(Create(t_plat), run_time=0.8)
        plat_lab = Text("= co-tenant lifetime", font_size=16, color=VLA).next_to(t_plat, UP, buff=0.1)
        self.play(FadeIn(plat_lab), run_time=0.6)

        # Thor onset marker
        t_mark = DashedLine(ax.c2p(LOCKOUT_THOR, 0), ax.c2p(LOCKOUT_THOR, 1.0), color=CONTROL, stroke_width=2)
        t_tag = Text(f"Thor  {LOCKOUT_THOR:g}%", font_size=16, color=CONTROL).next_to(ax.c2p(LOCKOUT_THOR, 0), DOWN, buff=0.5)
        # Orin companion onset at 8% (grey dashed)
        o_mark = DashedLine(ax.c2p(LOCKOUT_ORIN, 0), ax.c2p(LOCKOUT_ORIN, 1.0), color=GHOST, stroke_width=2)
        o_tag = Text(f"Orin  {LOCKOUT_ORIN:g}%", font_size=15, color=GHOST).next_to(ax.c2p(LOCKOUT_ORIN, 0), DOWN, buff=0.5).shift(LEFT * 0.3)
        self.play(Create(o_mark), FadeIn(o_tag), Create(t_mark), FadeIn(t_tag), run_time=1.2)

        bistable = Text("BISTABLE — no fair share", font_size=30, color=DANGER)
        bistable.to_edge(DOWN, buff=0.25)
        self.play(Write(bistable), run_time=1.2)

        tag = src_tag("params: lockout_onset_occupancy  (B.4)").to_corner(DR, buff=0.15)
        self.play(FadeIn(tag), run_time=0.5)

        used = 1.0 + 1.5 + 1.2 + 0.6 + 1.0 + 0.8 + 0.8 + 0.6 + 1.2 + 1.2 + 0.5
        self.wait(max(0.5, CLIP + 0.5 - used))
