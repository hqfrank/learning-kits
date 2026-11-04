# Explorers — rung 3 (learn-explorer)

Three single-file, no-build HTML explorers for the *wifi-csi-sensing* kit. Open one with a double-click or
`open 01-csi-vs-rssi-subcarriers.html`. They need no server, no network and no build step.

Each page inlines its parameters in a `<script type="application/json" id="params">` block, also shipped as
`params.json`, and renders them as a sources table. Entries of class `public` or `illustrative` are copied verbatim
from `../constants.json`, never retyped. Entries of class `assumption` are model choices one page makes to build its
synthetic signal (room size, reflectivities, scenario amplitudes, weights). They come from no study and are labelled
as such on the page. The kit carries **no measured numbers**, so no page has a measured overlay. Every signal is
synthetic, and every page says so in a banner.

The model of each page sits between `/*MODEL-START*/` and `/*MODEL-END*/`. It is pure, and it carries
`selfTest(P, assert)`. The page runs it with `console.assert` and prints the count under the sources table. The
same block is extracted with node `vm` for the checks below.

**Verification (2026-11-04):**
- Self-tests: 01 18/18, 02 11/11, 03 10/10, in the browser and under node.
- The node NaN sweep covered every select option × each slider's two extremes: 2.4 M numeric outputs, 0 non-finite.
  The node check also asserts that each inline params block equals `params.json` and `constants.json`.
- A Playwright sweep set every slider to min and max (one at a time and all together), with every select option,
  checkbox state and preloaded case, at 1280 px and 390 px. It found no NaN, Infinity or undefined in the visible text,
  no console errors and no horizontal overflow.
- `learning/stories/tools/shoot.py` passes on all three pages. Each page defines an empty `window.Story` stub,
  because explorers have no scenes and the shooter would otherwise throw.

**Reported back for the notes:** note B2 says a still room gives a lag-1 ACF "close to 1" and that motion lowers it.
That is true for the un-centred correlation of successive CSI reports. Explorer 02 uses the mean-removed ACF of the
WiDetect-style statistic that B2 cites, where a still room gives ≈ 0 and motion raises it. The information is the
same and the sign is opposite. The page states this convention.

---

## Spec — 01-csi-vs-rssi-subcarriers.html (notes A1, A2, B1)

```
Explorer: A moving body changes the shape of the CSI across subcarriers; RSSI keeps only the sum
Teaches:  H(f) = Σ a_i·exp(−j2πfτ_i). A body path adds to the static paths at a frequency-dependent angle, so some
          subcarriers rise while others fall. RSSI is one number (their sum). The extra information is the shape
          change, and it grows with channel width (finer delay resolution, A2). Also: the Fresnel zone of the body,
          the Doppler bound 2v/λ against the Nyquist limit of the report rate, and the B1 line fit removing CFO/STO.
Inputs:   band (5 / 2.4 GHz → wavelength_5g / wavelength_2g4); width (20/40/80 MHz → used_subcarriers_*);
          body position x −0.8…4.8 m, y −2.8…2.8 m (inside the 6 m × 6 m room); body reflectivity 0…0.4
          (assumption); walk direction; distance walked 0…0.5 m (several wavelengths); walking speed 0.1…2 m/s;
          report rate (csi_rate_beacon_illustrative / csi_rate_injected_illustrative); chip phase offsets on/off.
Outputs:  RSSI change at this step (dB); CSI shape change = std across subcarriers of the per-subcarrier dB change;
          max shape vs max RSSI change along the walk; Fresnel zone index of the body; first-zone radius ½√(λd);
          Doppler 2v/λ vs Nyquist R/2; sanitised phase (unwrap, subtract least-squares line).
Picture:  floor plan with TX, RX, first Fresnel ellipse, first-order wall paths, the body and its walk; |H| dB across
          subcarriers with and without the body plus both RSSI lines; sanitised phase (raw wrapped phase as dots);
          dB change vs distance walked for three subcarriers and RSSI.
Model:    LoS + image-method wall paths to second order (Γ^order·L/d) + body path γ·L·(1 m)/(d1·d2) (bistatic spreading,
          my simplification). Body blocking and diffraction not modelled.
Cases:    near the receiver (80 and 20 MHz), mid-link beside the LoS, far off the link, same walk at 2.4 GHz,
          1 m/s walk at beacon rate, slow 0.1 m/s motion at beacon rate.
Measured overlays: none (the kit has no measurements).
```

Self-tests: subcarrier counts 56/114/242; 64 × 312.5 kHz = 20 MHz; Fresnel r1 0.23 m (5 GHz) and 0.35 m (2.4 GHz)
on a 4 m link; delay resolution 50 ns / 15 m and 12.5 ns / 3.75 m; Doppler of a 1 m/s walk ≈ 36 Hz; beacon rate
9.77 Hz; Nyquist 5 Hz at 10 Hz; one path is frequency-flat; two paths fade every c/Δd; the line fit removes CFO + STO
exactly; the walk changes the shape; at 80 MHz the shape change exceeds the RSSI change; the body path is stronger
near a radio than mid-link; a uniform change has zero shape.

## Spec — 02-acf-variance-detector.html (notes A1, B2, B3, C1, C5)

```
Explorer: Window length and threshold trade latency against false alarms; ACF keeps its threshold across rooms
Teaches:  Sliding-window features (variance, mean-removed lag-1 ACF, averaged over subcarriers) with a threshold and
          an N-in-a-row rule give event-level detections, time to detect, time to clear and false alarms. Clearing
          waits about one window; onset can be faster. Variance carries the room's noise floor; the ACF does not.
          The ACF needs a report rate fast enough for the Doppler. A next-room walk and a fan both fire false alarms
          on one link. Alarms are converted to per month against the false-alarm budget.
Inputs:   report rate (10 / 100 Hz, illustrative); feature; window 0.5…8 s; ACF threshold 0…1 or variance threshold
          10⁻⁶…10⁻¹ (log); windows in a row 1…5; room noise σ 0.005…0.05 (assumption); walking speed 0.2…1.5 m/s;
          fan on/off.
Outputs:  person scenarios detected; false-alarm events (runs of touching positive windows outside person segments);
          window TPR/FPR; alarms per month = events / still seconds × seconds_per_30_days; per-scenario table.
Picture:  timeline: script bars, one subcarrier's amplitude, feature with threshold, decision band.
Model:    x_k(t) = (1 − slow shadowing)·|1 + Σ_m A/√M·exp(j(2π f_m t + φ))| + σ·n, with f_m spread up to 2v/λ (A1).
          Scenario script and amplitudes are assumptions.
Cases:    later studies (100 Hz, 4 s), early work (beacons, 1 s), variance in a quiet room, then a noisy room, ACF in
          the noisy room, fan in the empty home, low threshold with 3 in a row.
Measured overlays: none.
```

Self-tests: white-noise ACF ≈ 0; sinusoid ACF = cos(2πf/fs); Parseval (variance = spectrum without DC); 1% FPR at
1 s ≈ 25 920 false windows per month; budget 4 → per-window FPR ≈ 1.5 × 10⁻⁶; Nyquist 5 Hz; still-room ACF ≈ 0 in
quiet and noisy rooms; still variance scales with σ²; ACF lower at higher walking speed; scoring on a hand-made
sequence (time to detect 3 s, time to clear 1.5 s); N-in-a-row only removes positives.

## Spec — 03-two-endpoint-correlation.html (notes A1, B4)

```
Explorer: Is the motion at the AP or at a device? Cross-correlation of two AP links
Teaches:  Two links share the AP end. Motion near the AP moves both together (high ρ); motion near one device moves
          mostly its link (low ρ, that link wins by margin T); between the devices the answer is ambiguous. With AP
          links only, the AP's node variation w is never below a device's, so sorted nodes need correlation or
          device-to-device links. A wall scales the effect, but the system still reports motion (through-wall FP).
Inputs:   position along AP → device 1, 0…4 m; offset −3…3 m; next room (wall) on/off; sensor noise 0.02…0.5;
          activity threshold 1.2…10× the empty-room variance; ρ threshold 0…1; margin T 0…0.6.
Outputs:  each link's variance ÷ empty room (4 s window at 100 Hz, and expected); ρ (window and expected);
          normalised variation; node variation w; decision none / AP side / device 1 / device 2 / ambiguous.
Picture:  floor plan; the two link traces; expected ρ and variations along the AP → device 1 line with a decision band.
Model:    y_i = g·(c·s0 + e_i·s_i) + n·ε_i; c = proximity to the AP, e_i = proximity to device i + β·link-body term;
          proximity 1/(1+(d/r)²) with r = near_device_radius_illustrative; link-body term zero beyond
          single_link_range_illustrative. Phenomenological: the shared AP-end component is built in, as B4 describes.
Cases:    at the AP, near device 1, mid-link, toward device 2, between the devices, next room near device 1, far away.
Measured overlays: none.
```

Self-tests: 4 devices → 16 links; proximity = 0.5 at r; at the AP high ρ → AP side; near device 1 low ρ → device 1;
toward device 2 → device 2; empirical ρ and variance match expected; the wall scales motion variance by g²; w(AP) ≥
w(device) everywhere with AP links only; the equidistant point gives no single device; far and behind a wall → none.

---

## Files

| File | Teaches | Key inputs | Sources |
|---|---|---|---|
| `01-csi-vs-rssi-subcarriers.html` | The CSI shape change is what RSSI throws away, and it grows with width; Fresnel zone; Doppler vs report rate; phase sanitisation | band, width, body position, walk, speed, rate, offsets | notes A1, A2, B1; IEEE 802.11 counts and spacing |
| `02-acf-variance-detector.html` | Window and threshold trade latency for false alarms; ACF transfers across rooms, variance does not; next room and fans fire on one link | rate, feature, window, threshold, N in a row, noise, speed, fan | notes A1, B2, B3, C1, C5 |
| `03-two-endpoint-correlation.html` | Cross-correlation separates AP-side from device-side motion; the margin T; through-wall false positives | position, offset, wall, noise, thresholds, T | notes A1, B4 |
| `params.json` | every constant the pages load | — | `../constants.json` plus labelled page assumptions |
