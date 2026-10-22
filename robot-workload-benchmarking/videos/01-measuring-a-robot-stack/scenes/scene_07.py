from manim import *
from common import *

CLIP = 24.52


class Scene07(Scene):
    def construct(self):
        title = scene_title("Windows, gates, pre-registration")
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # Timeline: warm-up then window
        warm = Rectangle(width=2.6, height=0.6, fill_color=MUTED, fill_opacity=0.3,
                         stroke_color=MUTED)
        win = Rectangle(width=5.0, height=0.6, fill_color=TEAL, fill_opacity=0.25,
                        stroke_color=TEAL)
        tl = VGroup(warm, win).arrange(RIGHT, buff=0).move_to(UP * 1.9)
        warm_l = Text("warm-up 120 s", font_size=16, color=MUTED).move_to(warm.get_center())
        win_l = Text("window 300 s", font_size=17, color=TEAL).move_to(win.get_center())
        self.play(FadeIn(warm), FadeIn(warm_l), run_time=0.6)
        self.play(FadeIn(win), FadeIn(win_l), run_time=0.6)

        # five gate chips
        gates = ["alive", "expected rates", "crash scan", "census", "clocks"]
        chips = VGroup()
        for g in gates:
            chip = RoundedRectangle(width=2.1, height=0.6, corner_radius=0.25,
                                    stroke_color=GREEN, stroke_width=2, fill_opacity=0.12,
                                    fill_color=GREEN)
            t = Text(g, font_size=16, color=GREEN).move_to(chip.get_center())
            chips.add(VGroup(chip, t))
        chips.arrange(RIGHT, buff=0.25).move_to(UP * 0.5)
        for c in chips:
            self.play(FadeIn(c, scale=0.9), run_time=0.3)

        # ABBA interleave strip
        abba = VGroup()
        for i, ltr in enumerate("ABBA"):
            col = BLUE if ltr == "A" else ORANGE
            b = Square(side_length=0.6, fill_color=col, fill_opacity=0.3, stroke_color=col)
            t = Text(ltr, font_size=22, color=col).move_to(b.get_center())
            abba.add(VGroup(b, t))
        abba.arrange(RIGHT, buff=0.15).move_to(DOWN * 0.9 + LEFT * 3.0)
        abba_l = Text("interleaved: drift cancels", font_size=16, color=MUTED)
        abba_l.next_to(abba, DOWN, buff=0.2)
        self.play(FadeIn(abba), FadeIn(abba_l), run_time=0.7)

        # pre-register lock
        lock = Text("🔒", font_size=40).move_to(DOWN * 0.9 + RIGHT * 2.2)
        pr = VGroup(
            Text("pre-register:", font_size=18, color=FG),
            Text("hypotheses + thresholds frozen", font_size=16, color=MUTED),
            Text("no tuning after data", font_size=16, color=ROSE),
        ).arrange(DOWN, buff=0.15, aligned_edge=LEFT).next_to(lock, RIGHT, buff=0.3)
        self.play(FadeIn(lock), FadeIn(pr), run_time=0.8)

        tag = source_tag("120 s / 300 s illustrative · constants.json")
        self.play(FadeIn(tag), run_time=0.3)
        hold(self, CLIP)
