# YA DONYA: Cairo Reel (v4, transitions and typography rebuilt)

**Deliverable:** `Cairo_Ya_Donya_v2.mp4`: MP4 (mp42/isom, moov first), H.264 High@4.0 (avc1.640028), yuv420p, 1080×1920, 30 fps CFR, AAC-LC 48 kHz stereo (mp4a.40.2), 50.0 s, −14 LUFS / −1 dBTP.

## Lyrics (verified three ways: the soundtrack video's own captions, Whisper large-v3, and CTC forced alignment)
وميل وحدف منديله، كاتب على طرفه أجيله (×2)
وأمانة يا دنيا أمانة، تاخدينا للفرحة أمانة (×2)
وتخلّي الحزن بعيد عنّا، وتقولي للحب استنّا

Each word appears on its own aligned vocal onset (`tools/v3/lyrics_alignment.json`). Typeface: Aref Ruqaa (Ruqʿah, Egypt's handwriting script).
Verification note: in chorus 1 the singer repeats «أمانة» (heard as «وأمانة أمانة يا دنيا»). The captions show only «وأمانة / يا دنيا»; the film follows the audio.

## Structure
| Video time | Music | Picture |
|---|---|---|
| 0–1.97 | intro: Cairo's own sound (real horn, traffic) | Hook on the minaret square, 12-shot burst accelerating 8ths→16ths on the song's grid, riser |
| 1.97 | title slam | «القاهرة» lands, flare; the street is sucked out to silence |
| 2.4 | song enters alone | voice + balcony; the frame leans with «وميل» |
| 2.4–19.7 | verses A1/A2 | motorbike wipes on «منديله», «كاتب» written stroke by stroke, vanishing-point walks, whip pans, minaret ramp, real horn |
| 20.1–35.2 | chorus 1 & 2 | pulse on the chorus downbeat; «يا دنيا» opens on the minaret square (callback to the hook); Umm Kulthum mural |
| 35.2–38.0 | «تاخدينا للفرحة» | joy montage: six fast street shots on the beat |
| 38.0–40.0 | «أمانة» | lands on the elders through the shutter |
| 40.0–46.5 | outro | golden hour bus, then the station at sunset |
| 46.54 | «استنّا» (wait!) | the image freezes and the city goes silent; slow push; the held note blooms into a hall; CAIRO |

## Reproducing
`tools/v3/edl3.py` (edit + lyric timing), `render3.py` (compositor and typography), `audio3.py` (sound design).

## v4 revision
- **Handoff:** the burst's last flash is the balcony itself, so the film continues inside the same shot. The push-in never reverses, the street sound never drops out, and the first syllable swells out of the ambience.
- **Transitions:** synthetic whips, zoom pulses, frame roll and stutter are removed. Every cut is motivated (see `why` in `tools/v4/edl4.py`): direction-matched pans (a leftward current in verse 2, a rightward run in the joy montage), real vehicles carrying cuts (riders, car, motorbike, red SUV), and dissolves at three emotional turns.
- **Typography:** Amiri (a revival of the Bulaq Press type of 19th-century Cairo). Words are inked right-to-left on their vocal onsets. Kashida on the held notes is drawn for exactly as long as the singer holds them, in gold. A hairline breath-rule grows under each line. Each line clears before the next arrives, and lines are placed per shot away from faces.
