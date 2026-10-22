from manim import *
from common import *

CLIP = 20.75


class Scene05(Scene):
    def construct(self):
        title = scene_title("The bench: a second machine")
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # Robot (left, blue)
        robot = RoundedRectangle(width=4.6, height=4.0, corner_radius=0.15,
                                 stroke_color=BLUE, stroke_width=2.5, fill_opacity=0.05,
                                 fill_color=BLUE).move_to(LEFT * 3.3 + DOWN * 0.3)
        robot_t = Text("robot", font_size=22, color=BLUE).move_to(robot.get_top() + DOWN * 0.35)
        self.play(Create(robot), FadeIn(robot_t), run_time=0.8)

        robot_items = VGroup(
            Text("real stack", font_size=18, color=FG),
            Text("isolated control loop", font_size=18, color=RED),
            Text("observers · clock probe", font_size=16, color=VIOLET),
        ).arrange(DOWN, buff=0.35).move_to(robot.get_center() + DOWN * 0.2)
        for it in robot_items:
            self.play(FadeIn(it, shift=UP * 0.15), run_time=0.4)

        # Harness (right, orange)
        harness = RoundedRectangle(width=4.6, height=4.0, corner_radius=0.15,
                                   stroke_color=ORANGE, stroke_width=2.5, fill_opacity=0.05,
                                   fill_color=ORANGE).move_to(RIGHT * 3.3 + DOWN * 0.3)
        harness_t = Text("harness machine", font_size=20, color=ORANGE).move_to(
            harness.get_top() + DOWN * 0.35)
        self.play(Create(harness), FadeIn(harness_t), run_time=0.8)

        harness_items = VGroup(
            Text("fake motor boards", font_size=17, color=GREEN),
            Text("fake mic board", font_size=17, color=GREEN),
            Text("cloud stubs", font_size=17, color=GREEN),
            Text("synthetic people", font_size=17, color=GREEN),
        ).arrange(DOWN, buff=0.28).move_to(harness.get_center() + DOWN * 0.1)
        for it in harness_items:
            self.play(FadeIn(it, shift=UP * 0.12), run_time=0.35)

        # two links
        ctrl_link = Line(robot.get_right() + UP * 0.6, harness.get_left() + UP * 0.6,
                         color=RED, stroke_width=4)
        bulk_link = Line(robot.get_right() + DOWN * 0.8, harness.get_left() + DOWN * 0.8,
                         color=MUTED, stroke_width=3)
        ctrl_l = Text("control link", font_size=14, color=RED).next_to(ctrl_link, UP, buff=0.08)
        bulk_l = Text("bulk feed", font_size=14, color=MUTED).next_to(bulk_link, DOWN, buff=0.08)
        self.play(Create(ctrl_link), FadeIn(ctrl_l), run_time=0.5)
        self.play(Create(bulk_link), FadeIn(bulk_l), run_time=0.5)

        note = Text("harness on a SECOND machine — it does not steal compute",
                    font_size=18, color=ORANGE).to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note), run_time=0.6)

        tag = source_tag("harness · note C3")
        self.play(FadeIn(tag), run_time=0.3)
        hold(self, CLIP)
