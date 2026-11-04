# A1 — CSI: subcarriers, multipath, and what a moving body does

**Source:** IEEE 802.11 OFDM PHY (subcarrier spacing and counts); Ma, Zhou, Wang, Computing Surveys (CSUR) 2019 §2 (CSI model); Wang et al., UbiComp 2016 (Fresnel-zone model); Wang et al., MobiCom 2015 (CARM, CSI-speed model); Qian et al., MobiHoc 2017 (Widar, Doppler). Single-link observations from internal I1 §3.4, generalised. · **Status:** concept note.

## In one sentence
CSI is the receiver's estimate of the channel's complex gain at each OFDM subcarrier for each transmit–receive antenna pair, and a moving body changes the length of some propagation paths, which makes the CSI amplitude and phase fluctuate in a pattern that a single signal-strength number cannot show.

## What it is
**OFDM (orthogonal frequency-division multiplexing)** splits a Wi-Fi channel into many narrow **subcarriers**. In 802.11a/n/ac the subcarriers are 312.5 kHz apart (`ofdm_subcarrier_spacing_11a_n_ac`). A 20 MHz channel uses a 64-point FFT and 52 subcarriers in 802.11a/g, or 56 in 802.11n (`used_subcarriers_legacy_20MHz`, `used_subcarriers_ht_20MHz`). Each frame starts with known **training symbols**. The receiver compares what it received with what it knows was sent. The ratio is the channel estimate.

**Channel state information (CSI)** is that estimate. For one frame it is a complex matrix with one entry per subcarrier per antenna pair:

- the **amplitude** |H| says how much the channel attenuated that subcarrier;
- the **phase** ∠H says how much it delayed it.

The receiver needs CSI anyway to equalise the frame. Sensing only asks the chip to hand it to software.

**RSSI (received signal strength indicator)** is one number per frame: the total received power, summed over the whole channel. RSSI is a MAC-layer summary. CSI is the PHY-layer detail behind it (internal I1 §2; Ma et al. 2019).

## How it works
**Multipath.** Indoors, the signal reaches the receiver by many paths: the direct line of sight (LoS), reflections from walls, floor, furniture, and people. Each path *i* has an attenuation *aᵢ* and a delay *τᵢ*. The CSI at subcarrier frequency *f* is the sum of the paths, each rotated by its delay:

H(f) = Σᵢ aᵢ · exp(−j 2π f τᵢ)

Because the rotation depends on *f*, the paths add up differently at each subcarrier. Some subcarriers sit in a deep fade and some in a peak. This **frequency-selective fading** is the "fingerprint" that RSSI averages away.

**Static and dynamic paths.** Split the sum into a static part (walls, furniture) and a dynamic part (paths that bounce off the moving person). The static part is constant. When the person moves, the dynamic path length changes, its phase rotates, and the dynamic part adds to the static part with a changing angle. The amplitude therefore rises and falls (Wang et al. 2015, CARM).

Analogy: the multipath field is a spider's web. A fly landing anywhere makes the threads tremble; the pattern of trembling says roughly where it landed.

**Speed and Doppler.** One full cycle of amplitude fluctuation happens when the dynamic path length changes by one wavelength. The wavelength is about 12.3 cm at 2.4 GHz and about 5.5 cm at 5 GHz (`wavelength_2g4`, `wavelength_5g`, my arithmetic). For a reflected path, the path length changes at up to twice the body speed. An illustrative walk at 1 m/s therefore produces fluctuations up to about 36 Hz at 5 GHz (`doppler_walk_example_5g`, my arithmetic). Widar and WiDance use this **Doppler** frequency to estimate speed and direction (Qian et al. 2017).

- **Caution:** a CSI stream sampled at an illustrative 10 Hz (`csi_rate_beacon_illustrative`) cannot represent fluctuations above 5 Hz. At beacon rates the detector sees aliased energy and envelope changes, not a clean Doppler spectrum (my explanation, Nyquist). This is why the sampling rate matters in [[A2-what-the-hardware-gives-you]].

**Fresnel zones.** The **Fresnel zones** of a link are nested ellipsoids with the transmitter and receiver at the foci. The *n*-th zone boundary is where a reflected path is *n* half-wavelengths longer than the LoS. The first zone carries most of the energy. Its radius at the link midpoint is ½·√(λ·d). For an illustrative 4 m link (`link_length_illustrative`) this is about 0.23 m at 5 GHz and about 0.35 m at 2.4 GHz (`fresnel_first_zone_mid_radius_example`, my arithmetic). A person who crosses zone boundaries produces a fluctuation per boundary; a person inside the first zone blocks and diffracts the LoS (Wang et al. 2016).

**What a single link sees.** A power-fading simulation (propagation + diffraction + body absorption) and single-link measurements agreed on three patterns (internal I1 §3.4):

1. Motion close to either radio changes the CSI most.
2. Motion on the LoS causes a larger power drop than motion beside it.
3. On the LoS, motion in the middle of the link changes the CSI *less* than motion near the ends. The first Fresnel zone is narrowest near the radios, so a body there occupies a larger fraction of it (my explanation).

The measured sensitivity fell steeply outside the first Fresnel zone. Walking became hard to see beyond an illustrative 4 m from the LoS (`single_link_range_illustrative`). A wall between the motion and the link removed most of the effect (internal I1 §3.4).

**Antenna pairs.** A device with 2 transmit and 2 receive antennas measures 4 antenna-pair channels (`mimo_2x2_streams`). The pairs see different multipath, which gives some angular selectivity. A single-antenna device averages all directions into one channel (internal I7).

## Common confusions
- **"CSI is just a finer RSSI."** RSSI is roughly the power summed over subcarriers. CSI keeps the per-subcarrier shape, which encodes the multipath geometry. Two very different motions can give the same RSSI change and different CSI changes.
- **"Phase is the better signal because it is more precise."** On commodity chips the raw phase carries large random offsets per frame (see [[A2-what-the-hardware-gives-you]] and [[B1-preprocessing]]). Without sanitisation the amplitude is the more usable signal.
- **"The middle of the link is the most sensitive spot."** The ends are more sensitive than the middle (internal I1 §3.4; Fresnel geometry).
- **"More subcarriers means more independent measurements."** Adjacent subcarriers are strongly correlated. The useful diversity is set by the delay spread of the room, not by the subcarrier count (my explanation; see the grouping result in [[B1-preprocessing]]).

## Why it matters
Every later design choice follows from this model. Sensitivity is highest near the radios and along the LoS, so placement decides coverage. Motion changes the dynamic part only, so removing the static part (the mean, the DC term) is what makes features portable across homes ([[B2-features]]). Sampling rate limits which motions are visible ([[A2-what-the-hardware-gives-you]]).

## Terms introduced
- **OFDM** — a modulation that splits a channel into many orthogonal narrow subcarriers.
- **subcarrier** — one narrow frequency tone of an OFDM channel.
- **training symbols** — the known part of a frame's preamble that the receiver uses to estimate the channel.
- **CSI (channel state information)** — the complex channel gain per subcarrier per antenna pair, estimated from one frame.
- **amplitude / phase (of CSI)** — the magnitude and angle of one CSI entry.
- **RSSI** — one received-power value per frame.
- **multipath** — propagation by several paths with different delays.
- **frequency-selective fading** — the variation of channel gain across subcarriers caused by multipath.
- **static / dynamic paths** — paths whose length does not / does change with motion.
- **line of sight (LoS) / non-line of sight (NLoS)** — the direct path between radios exists / is blocked.
- **Doppler (frequency)** — the rate of phase rotation of a path whose length changes, in Hz.
- **Fresnel zone** — an ellipsoid around a link where a reflected path is a whole number of half-wavelengths longer than the LoS.
- **antenna pair** — one transmit antenna and one receive antenna; each pair has its own CSI.
