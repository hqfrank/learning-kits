from manim import *
from common import *

CLIP = 26.20


class Scene04(Scene):
    def construct(self):
        title = scene_title("Measure each service alone: three levels")
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # Nested boxes: L1 inside L2 inside L3, left of centre
        l3 = RoundedRectangle(width=5.6, height=4.2, corner_radius=0.15,
                              stroke_color=SKY, stroke_width=2.5, fill_opacity=0.05,
                              fill_color=SKY)
        l2 = RoundedRectangle(width=4.0, height=3.0, corner_radius=0.12,
                              stroke_color=BLUE, stroke_width=2.5, fill_opacity=0.07,
                              fill_color=BLUE)
        l1 = RoundedRectangle(width=2.4, height=1.6, corner_radius=0.1,
                              stroke_color=GREEN, stroke_width=2.5, fill_opacity=0.12,
                              fill_color=GREEN)
        nest = VGroup(l3, l2, l1).move_to(LEFT * 3.2 + DOWN * 0.3)

        l1_t = Text("L1 engine", font_size=18, color=GREEN).move_to(l1.get_center())
        l2_t = Text("L2 deployed", font_size=17, color=BLUE).move_to(l2.get_top() + DOWN * 0.3)
        l3_t = Text("L3 + upstream", font_size=17, color=SKY).move_to(l3.get_top() + DOWN * 0.3)

        self.play(Create(l3), FadeIn(l3_t), run_time=0.7)
        self.play(Create(l2), FadeIn(l2_t), run_time=0.7)
        self.play(Create(l1), FadeIn(l1_t), run_time=0.7)

        # gap brackets on the right of the nest
        g1 = Text("L2 − L1 = service glue", font_size=19, color=AMBER)
        g2 = Text("L3 − L2 = real-input cost", font_size=19, color=AMBER)
        gaps = VGroup(g1, g2).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        gaps.move_to(RIGHT * 2.6 + UP * 1.4)
        self.play(FadeIn(g1, shift=LEFT * 0.2), run_time=0.6)
        self.play(FadeIn(g2, shift=LEFT * 0.2), run_time=0.6)

        glue_note = Text("glue usually costs more\nthan the network", font_size=17,
                         color=MUTED, line_spacing=0.8)
        glue_note.next_to(gaps, DOWN, buff=0.4).align_to(gaps, LEFT)
        self.play(FadeIn(glue_note), run_time=0.6)

        # idle floor vs working cost side panel
        base = DOWN * 2.1 + RIGHT * 2.6
        idle = Rectangle(width=0.7, height=0.25, fill_color=ROSE, fill_opacity=0.5,
                         stroke_color=ROSE).move_to(base + LEFT * 0.8)
        work = Rectangle(width=0.7, height=1.4, fill_color=GREEN, fill_opacity=0.5,
                         stroke_color=GREEN).move_to(base + RIGHT * 0.8 + UP * 0.57)
        idle_l = Text("idle floor", font_size=15, color=ROSE).next_to(idle, DOWN, buff=0.12)
        work_l = Text("driven", font_size=15, color=GREEN).next_to(work, DOWN, buff=0.12)
        work_l.align_to(idle_l, DOWN)
        self.play(GrowFromEdge(idle, DOWN), FadeIn(idle_l),
                  GrowFromEdge(work, DOWN), FadeIn(work_l), run_time=0.9)

        tag = source_tag("levels · note C2")
        self.play(FadeIn(tag), run_time=0.3)
        hold(self, CLIP)
