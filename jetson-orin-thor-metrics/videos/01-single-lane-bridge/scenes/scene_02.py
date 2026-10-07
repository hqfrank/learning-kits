"""Scene 02 — The datasheet says there's room. Narration ~32.0 s."""
from manim import *
from theme import (BG, VLA, CONTROL, INK, GHOST, DANGER,
                   NVFP4_MEAS, NVFP4_DATASHEET, INT8FP8_DATASHEET, TCGEN05_FP16, src_tag)

CLIP = 32.03


class Scene02(Scene):
    def construct(self):
        self.camera.background_color = BG
        title = Text("The datasheet says there's room", font_size=38, color=INK).to_edge(UP, buff=0.5)
        self.play(FadeIn(title, shift=DOWN * 0.3), run_time=1.0)

        # horizontal bar scale: 0 .. 1035 TFLOP/s mapped to a 9-unit-wide axis
        X0 = -3.4
        FULL_W = 7.6
        MAXV = 1100.0

        def bar(value, color, dashed=False, opacity=0.9):
            w = FULL_W * value / MAXV
            r = Rectangle(width=max(w, 0.02), height=0.5,
                          stroke_color=color, fill_color=color,
                          fill_opacity=0.0 if dashed else opacity, stroke_width=2)
            if dashed:
                r = DashedVMobject(r, num_dashes=int(max(w, 0.1) * 6) + 4)
            r.move_to([X0 + w / 2, 0, 0])
            return r

        rows = [
            ("NVFP4 dense", NVFP4_DATASHEET, NVFP4_MEAS, "60.7%", VLA),
            ("INT8 / FP8", INT8FP8_DATASHEET, 324.5, "~63%", VLA),
            ("FP16 (tcgen05)", 258, TCGEN05_FP16, "75%", VLA),
        ]

        y = 1.7
        made = []
        for name, ds, meas, frac, col in rows:
            ds_bar = bar(ds, GHOST, dashed=True)
            meas_bar = bar(meas, col)
            ds_bar.shift(UP * y)
            meas_bar.shift(UP * y)
            lab = Text(name, font_size=18, color=INK)
            lab.move_to([X0 - 1.5, y, 0])
            ds_val = Text(f"datasheet {ds:g}", font_size=14, color=GHOST).next_to(ds_bar, RIGHT, buff=0.15)
            meas_val = Text(f"measured {meas:g}  ({frac})", font_size=15, color=col)
            meas_val.next_to(meas_bar, UP, buff=0.05).align_to(meas_bar, LEFT).shift(RIGHT * 0.1)
            self.play(FadeIn(lab), Create(ds_bar), run_time=0.7)
            self.play(GrowFromEdge(meas_bar, LEFT), FadeIn(ds_val), run_time=0.9)
            self.play(FadeIn(meas_val), run_time=0.5)
            made += [lab, ds_bar, meas_bar, ds_val, meas_val]
            y -= 1.15

        unit = Text("TFLOP/s  (Thor, tcgen05 / NVFP4)", font_size=15, color=GHOST)
        unit.move_to([X0 + 3.5, y - 0.1, 0])
        self.play(FadeIn(unit), run_time=0.6)

        # the control loop: a tiny dot near zero
        dot = Dot([X0 + 0.05, y - 0.9, 0], radius=0.08, color=CONTROL)
        dot_lab = Text("control loop needs ~this", font_size=16, color=CONTROL).next_to(dot, RIGHT, buff=0.2)
        self.play(FadeIn(dot, scale=0.5), FadeIn(dot_lab), run_time=1.0)

        caption = Text("TOPS is not the constraint", font_size=28, color=INK)
        caption.to_edge(DOWN, buff=0.55)
        self.play(Write(caption), run_time=1.2)

        tag = src_tag("params: nvfp4_dense_ceiling, tensor_tcgen05_fp16").to_corner(DR, buff=0.2)
        self.play(FadeIn(tag), run_time=0.5)

        used = 1.0 + 3 * (0.7 + 0.9 + 0.5) + 0.6 + 1.0 + 1.2 + 0.5
        self.wait(max(0.5, CLIP + 0.5 - used))
