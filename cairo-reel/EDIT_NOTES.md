# CAIRO CLOCKWORK: Instagram Reel (v2, complete re-edit)

**Deliverable:** `Cairo_Clockwork.mp4`: MP4 (mp42), H.264 High@4.0, yuv420p, 1080×1920, 30 fps CFR, ~10 Mbps, AAC-LC 256 kbps 48 kHz, fast start, 46.4 s, −14 LUFS / −1 dBTP. Loops seamlessly.

## Concept
Cairo as a living mechanism. The mechanical sounds (from the BOOM *Mechanicals* teaser in the Sound Effects folder) are the film's spine. They only appear where **time itself is manipulated**: when the machine starts (opening), when the clock skips (midpoint) and when it winds down (ending). Everywhere else the city speaks with its own recorded sound.

## Soundtrack map (measured)
Nine vocal lines: 0.13 / 4.98 / 9.31 / 14.69 / 23.48 (B section, higher register) / 27.88 / 32.82 / 37.52 (peak pitch) / 41.55. Strong accents at 4.99 and 32.86. The source file cuts off mid-note at 46.0, so the ending is designed around it.

## Structure and transition reasoning
| Time | Sequence | Transition and why |
|---|---|---|
| 0–4.99 | **Opening (IMPORTANT recreation):** mural hook, 9×3-frame preview burst, books detail, balcony title, light-leak burn | Mechanical clunk starts the machine; a watch tick on every flash cut, as in the reference; dissolve; **title struck letter by letter with real typewriter keys**; burn hides the cut on the 4.99 accent |
| 4.99–9.31 | **The Walk:** four forward-walking streets | Cuts on the beat with the **vanishing point locked**: one continuous walk through four neighbourhoods |
| 9.31–14.06 | **Street life:** shutter, café, bread stand | Breathing hard cuts; café → bread continues the same pan direction |
| 14.06–22.0 | **Vehicles carry us** | Object wipes on passing motorbikes and cars; a motorbike hands over to a motorbike |
| 22.0–23.8 | **Through the door** | SUV wipe; push into the arched doorway; the **real doorway becomes the mask** revealing Old Cairo; latch click on the B-section entry |
| 23.5–27.9 | **Old Cairo** | Minaret tilt-down → stone minaret (shape match) → man walking right |
| 27.9–32.86 | **Grandeur → the clock skips** | Rightward pan follows his direction; then stop-motion steps with ratchet clicks; the city falls silent in a freeze; wind-up; release on the 32.86 accent |
| 32.86–37.5 | **Release** | Speed-ramped minarets → minaret at the vanishing point → passer-by wipe |
| 37.5–41.55 | **Climax** | No effects: two long golden-hour holds; the music takes control |
| 41.55–46.4 | **Wind-down** | Reverse pan decelerates onto the exact opening frame; tape-stop, slowing ratchet, final latch; loops to the start |

## Image
iPhone HLG HDR → SDR via proper tone-mapping (zimg linearisation + Hable). Natural grade: gentle contrast, +5% saturation, minimal warmth; per-shot exposure and white balance matched to the film's median, with intentional golden-hour warmth kept. Light vignette and fine grain.

## Sound
Each shot's own sync sound (traffic, motorbikes, crowds), loudness-matched and crossfaded at every cut. It swells in every vocal gap and on each passing vehicle, drops back under the climax, is chopped with the stop-motion, and goes silent in the freeze.

## Reproducing
`tools/v2/edl2.py` (edit decision list), `render2.py` (compositor, reads graded intermediates), `audio2.py` (sound design and mix; every event is derived from the EDL).
