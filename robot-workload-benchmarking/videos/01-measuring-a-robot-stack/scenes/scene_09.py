from manim import *
from common import *


class Scene09(Scene):
    def construct(self):
        title = Text("Sources", font_size=40, color=FG, weight=BOLD).to_edge(UP, buff=0.6)
        self.play(FadeIn(title), run_time=0.8)

        lines = VGroup(
            Text("This kit's constants.json / params.json — illustrative + public values",
                 font_size=20, color=FG),
            Text("Notes A0, B0, B2, C1–C7 (robot-workload-benchmarking)",
                 font_size=20, color=MUTED),
            Text("Public docs: Linux cgroups v2 / CFS bandwidth, ROS 2 concepts",
                 font_size=20, color=MUTED),
            Text("SNTP (RFC 4330), NVIDIA Nsight Systems / Compute",
                 font_size=20, color=MUTED),
            Text("No measured robot or campaign number appears.",
                 font_size=20, color=ROSE),
            Text("Rung 4 of 4: notes → diagram → explorer → video",
                 font_size=18, color=TEAL),
        ).arrange(DOWN, buff=0.4, aligned_edge=LEFT)
        lines.move_to(DOWN * 0.3)

        for ln in lines:
            self.play(FadeIn(ln, shift=UP * 0.1), run_time=0.5)
        self.wait(3.0)
