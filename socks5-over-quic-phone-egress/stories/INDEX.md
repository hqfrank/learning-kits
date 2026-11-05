# Stories — SOCKS5 over QUIC through the phone

Picture-first, interactive pages. Open one before the notes to get the mental model; the notes stay
the reference.

| Story | Teaches | Spec |
|---|---|---|
| [01 — The house line](01-the-house-line.html) | Why cloud addresses get screened; one SOCKS5 CONNECT end to end with remote DNS (`socks5h`) and passthrough; one QUIC connection with a stream per call (head-of-line blocking, the stream cap); the phone dials out, the anycast port map, keepalive below the NAT timeout, migration; trust from a pinned fingerprint, ALPN and a single-use token; five guards (filter after DNS, metadata, amplification, handshake floods, ports and localhost); deadlines, invisible fallback and the commit point. | [spec](01-the-house-line.spec.md) |

## Rubric scores (story.md §9, 1–5)

| Story | Answer-first | Metaphor fidelity | Motion meaning | Text economy | Interaction | Truth | Craft | Access |
|---|---|---|---|---|---|---|---|---|
| 01 | 5 | 4 | 4 | 4 | 5 | 5 | 4 | 4 |

Notes on the scores:

- **Answer-first 5.** The hero shows the whole design: the far office's screened call (coral, "prove you're human"), the trunk line from the house through the front desk, the helper with the local directory and a crossed-out intercom, the shop's caller ID reading "your home", and the usual line carrying the letter. Five tickets under it link B1, B2, B3, B4/B5 and C1.
- **Metaphor fidelity 4.** The brief's courier carries letters (packets), which suggests a layer-3 tunnel. A telephone exchange relays *connections*, so "you're connected" (REP 0x00), the commit point, a trunk with channels (streams), caller ID (source IP), the local directory (remote DNS), "nobody rings into a house" (NAT) and the click that keeps a line remembered (keepalive) map one to one. The brief's voiceprint-over-a-trusted-channel and refused-rooms ideas stay. It loses a point because the helper really *is* a phone, and because a voice can be imitated where a fingerprint cannot; five "where it breaks" items are in the footer.
- **Motion 4.** Calls ride the trunk and the house line in the hero; the letter travels the usual line. In scenes, tokens carry the request onto channel 1, the dial-out from the house, the office's channel requests back on the same line, the migrated path over the mast, and the ticket on channel 0. The cost bar grows. Still mode shows riders mid-path.
- **Text economy 4.** Captions are one bold claim plus one or two sentences; scene 7's step 1 caption is at the upper limit.
- **Interaction 5.** Four predicts with a plausible wrong answer each (the branch near you, 1 and 1, "the helper only compares prints", "switch lines quietly"). Two live figures: who looks it up and which check refuses (2 schemes × 6 destinations × 3 ports, following explorer 01's rules), and click interval vs idle timeout vs the RFC 9308 NAT assumption. Six scene players, five flip cards.
- **Truth 5.** 38 kit entries are inlined verbatim from `../constants.json` and `../explorers/params.json` by a generator that scans the page for keys; three `story_*` picture values (six calls with one loss, the B3 example port map, the port list) carry class and source. Captions pull numbers through `{{key}}` placeholders. Self-tests (`console.assert`) reproduce: 40 USD vs 0.10 USD for 5 GB (B3); the CONNECT deadline exceeds 10 + 8 s (C2); 3 × 1200 = 3600 (C1); keepalive below 30 s and at most a third of the idle timeout (B2); 7 + 15 = 22 bytes (B1); socks5h vs socks5 branch choice; rebinding, hex, short form, IPv4-mapped and port 22 refusals; every combination ends with one reply; the keepalive cases of explorer 03.
- **Craft 4.** One palette (leaf = your home, coral = refused, sky = trunk, sun = directory and deadlines, plum = trust, stone = office) and navy outlines. Verified with `shoot.py` (no console errors, no failed asserts, no overflow at 1280 px or 390 px, 29 steps) and an extra Playwright pass: four answered predicts, the live figures at five and four settings, the engineer view of the hero and four scenes, a flipped card. Fixes during verification: two step labels printed on top of each other on the trunk (`st-at`), the mast label crossing the trunk, a lane line striking through a label, the hang-up limit drawn over the memory row, the "hung up" mark on the axis labels, the office icon colliding with a row label, empty card fronts.
- **Access 4.** Scene players work from the keyboard (←/→); every SVG has `role="img"` and an `aria-label` or `<title>`; captions and readouts are `aria-live`; selects and sliders are labelled; a Motion-off switch; verdicts are written out (✓/✗ plus words), never colour only. Contrast was not measured with a tool.

## Credits

Shared runtime ideas adapted from [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer)
(MIT): the stepper/scene player, one pure model per live figure, figures lead and words label.
Narrative shape from Nicky Case, [How I make explorable explanations](https://blog.ncase.me/how-i-make-an-explorable-explanation/).
One idea per scene from [geeklee/srt-whiteboard-animation](https://github.com/geeklee/srt-whiteboard-animation).
Metaphor seed ("the courier who posts letters from your home", the badge checked against a photo from a
trusted channel, the refused inner rooms) from the kit brief, moved to a telephone exchange.
