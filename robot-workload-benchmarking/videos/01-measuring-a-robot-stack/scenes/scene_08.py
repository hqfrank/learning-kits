from manim import *
from common import *

CLIP = 24.95


class Scene08(Scene):
    def construct(self):
        title = scene_title("Combine and attribute the first limit")
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        base = DOWN * 1.2
        # solo bars stacked -> summed
        solo1 = Rectangle(width=0.8, height=0.9, fill_color=SKY, fill_opacity=0.5,
                          stroke_color=SKY)
        solo2 = Rectangle(width=0.8, height=0.7, fill_color=AMBER, fill_opacity=0.5,
                          stroke_color=AMBER)
        solo3 = Rectangle(width=0.8, height=0.6, fill_color=VIOLET, fill_opacity=0.5,
                          stroke_color=VIOLET)
        solos = VGroup(solo1, solo2, solo3).arrange(RIGHT, buff=0.3)
        solos.move_to(LEFT * 3.8 + base + UP * 0.5)
        for s in solos:
            s.align_to(solos, DOWN)
        solo_l = Text("solo runs", font_size=18, color=MUTED).next_to(solos, DOWN, buff=0.3)
        self.play(*[GrowFromEdge(s, DOWN) for s in solos], FadeIn(solo_l), run_time=0.9)

        # summed bar
        summed = Rectangle(width=0.9, height=2.2, fill_color=MUTED, fill_opacity=0.4,
                           stroke_color=MUTED).move_to(LEFT * 1.0 + base + UP * 1.1)
        sum_l = Text("sum of solos", font_size=16, color=MUTED).next_to(summed, DOWN, buff=0.3)
        self.play(FadeIn(summed, shift=UP * 0.2), FadeIn(sum_l), run_time=0.7)

        # combined bar (taller)
        combined = Rectangle(width=0.9, height=3.0, fill_color=ROSE, fill_opacity=0.45,
                             stroke_color=ROSE).move_to(RIGHT * 0.7 + base + UP * 1.5)
        comb_l = Text("combined", font_size=16, color=ROSE).next_to(combined, DOWN, buff=0.3)
        self.play(GrowFromEdge(combined, DOWN), FadeIn(comb_l), run_time=0.8)

        iff = Text("interference factor = combined / solo", font_size=19, color=ROSE)
        iff.to_edge(UP, buff=1.4)
        self.play(FadeIn(iff), run_time=0.6)

        # CPU fills before GPU
        cpu = Rectangle(width=0.7, height=2.4, stroke_color=BLUE, fill_opacity=0).move_to(
            RIGHT * 3.5 + base + UP * 1.2)
        cpu_fill = Rectangle(width=0.7, height=2.4, fill_color=BLUE, fill_opacity=0.6,
                             stroke_color=BLUE).move_to(cpu.get_center())
        gpu = Rectangle(width=0.7, height=2.4, stroke_color=GREEN, fill_opacity=0).move_to(
            RIGHT * 4.6 + base + UP * 1.2)
        gpu_fill = Rectangle(width=0.7, height=1.2, fill_color=GREEN, fill_opacity=0.6,
                             stroke_color=GREEN)
        gpu_fill.move_to(gpu.get_bottom() + UP * 0.6)
        cpu_l = Text("CPU", font_size=16, color=BLUE).next_to(cpu, DOWN, buff=0.3)
        gpu_l = Text("GPU", font_size=16, color=GREEN).next_to(gpu, DOWN, buff=0.3)
        self.play(Create(cpu), Create(gpu), FadeIn(cpu_l), FadeIn(gpu_l), run_time=0.6)
        self.play(GrowFromEdge(cpu_fill, DOWN), GrowFromEdge(gpu_fill, DOWN), run_time=0.9)

        note = Text("often CPU quota fills before GPU", font_size=19, color=BLUE)
        note.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(note), run_time=0.6)

        tag = source_tag("interference factor · note C6")
        self.play(FadeIn(tag), run_time=0.3)
        hold(self, CLIP)
