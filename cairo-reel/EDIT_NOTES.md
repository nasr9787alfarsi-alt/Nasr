# Cairo Street Experience: Instagram Reel

**Deliverable:** `Cairo_Reel.mp4`: 1080×1920 (9:16), 30 fps, H.264 High, 23.0 s, AAC 320 kbps, −14 LUFS / −1 dBTP.

## Opening: recreation of the "IMPORTANT" reference
| Reference (IMPORTANT) | This reel | Music anchor |
|---|---|---|
| 0–0.67 s "CAIRO" poster hook | 0–0.77 s Umm Kulthum mural (Cairo's icon) | first vocal onset 0.77 |
| 0.67–1.57 s nine 3-frame preview flashes | 0.77–1.67 s nine 3-frame flashes of shots that appear later | on the phrase |
| 1.57–2.27 s detail hold → dissolve | 1.67–2.64 s Islamic-Cairo minaret hold → dissolve | phrase gap 2.49–2.58 |
| 2.27–4.17 s top-down coffee + typed "VISUAL DIARY from Egypt" | 2.64–4.25 s balcony over downtown + typed "VISUAL DIARY from Cairo" | onset 2.64 |
| 4.17–4.47 s light-leak burn | 4.11–4.47 s light-leak burn, cut hidden at its peak | onset 4.11 |
| arch-window mask near the end | arch-window reveal in the song's silence 9.6–10.3 | vocal re-entry 10.30 |
| ends on the opening CAIRO sign | final hit lands on the opening mural (bookend; loops cleanly) | hit 20.51 |

## Structure
- **Development (4.3–9.6 s):** calm phrase-length holds: walking into the street, ornate balconies, old men through a wooden shutter, book kiosk, bread stand.
- **Breath (9.6–10.3 s):** the music falls silent; the city's own sound rises while an arch window opens onto a minaret.
- **Build (10.3–17.1 s):** speed-ramped tilt-down from minaret to street, then accelerating cuts on vocal onsets. Three invisible wipes on objects passing the lens (motorbike 12.27, SUV 14.75, motorbike 17.10).
- **Climax (17.1–20.1 s):** the long held note goes from day into golden hour: minarets pan (ramp), blue bus at sunset, the station with the flag.
- **Ending:** 0.4 s of silence (only the station crowd), then the final hit lands on the mural bookend, fades to black, and an end card (القاهرة · CAIRO) plays during the ring-out.

## Image
iPhone HLG HDR → SDR via proper tone-mapping (zimg linearisation + Hable). Then a gentle grade: soft S-curve with lifted blacks, warm highlights and cool shadows, +12% saturation, a subtle vignette and fine monochrome grain. Shadows aren't crushed, and nothing is darkened artificially.

## Sound
The provided track is the only music. Each shot's own sync sound (real Cairo traffic, crowds, motorbikes) is loudness-matched and crossfaded under it at about −15 to −19 dB, and swells in the two silences. Two very low filtered-air whooshes sit under the light leak and the tilt ramp.

## Reproducing
`tools/edl.py` is the full edit decision list. `tools/render.py` composites the frames (it expects graded intermediates in `inter/`). `tools/audio_mix.py` builds the mix.
