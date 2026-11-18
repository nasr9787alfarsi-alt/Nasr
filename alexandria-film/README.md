# ALEXANDRIA — The Mediterranean Experience

A cinematic travel film of a two-day trip to Alexandria, Egypt (17–18 November 2026),
cut to *Ala Bali* by Aida El Ayoubi.

## Source material

- 75 iPhone clips: vertical 1080×1920, HEVC 10-bit, HDR (HLG / BT.2020), 30 fps
- The song: 5:15, AAC 128 kb/s

## Deliverables

| File | Use |
|---|---|
| `Alexandria_Film_HEVC.mp4` | Main master: HEVC 10-bit, Rec.709 SDR, AAC 320k |
| `Alexandria_Film_H264.mp4` | Maximum compatibility (WhatsApp, Instagram, Windows) |
| `Alexandria_Film_HDR_HLG.mp4` | The original iPhone HDR look, for HDR screens |

All three are 1080×1920, 30 fps, 2:34. The masters are cut from 10-bit ProRes 422 HQ
intermediates.

**Why vertical and not 4K 16:9:** every source clip is vertical 1080p. A 16:9 frame would mean
either cropping each shot to about a third of its frame and upscaling it about 3.5×, or
pillarboxing on a blurred background. Both throw away the image quality the brief puts first,
so the film keeps the native frame with no upscaling.

## Music edit

- Tempo is 117.5 BPM (one beat is 0.511 s).
- The section that starts at 106.0 s returns exactly 312 beats later, at 264.7 s.
- The song is spliced on matching beats, 116.17 s → 274.83 s, with a 30 ms equal-power
  crossfade. The splice measures 0.99 on beat-synchronous chroma + MFCC similarity.
- The result keeps the free intro, the band drop, the first two sections, the peak and the
  original outro, at 2:33.
- The splice sits inside a single held night shot, so no picture cut points at it.
- The mix is normalised to −14 LUFS integrated and −1 dBTP.
- Natural sound from the clips is high-passed at 180 Hz to remove wind and kept low under the
  music: the platform, the approaching and passing train, and the sea under the end card.

## Structure

| Film time | Music | Picture |
|---|---|---|
| 0:00–0:13 | free intro | Dawn platform → the traveller watching the train → headlight approaching |
| 0:13 | band drop | Train blasts past |
| 0:13–0:49 | verse | Window views and fields → arriving at the station → square, taxis |
| 0:49 | section hit | Sea reveal from above, with the **ALEXANDRIA** title |
| 0:57–1:13 | rhythm | Streets cut on the beat |
| 1:13–1:42 | accent at 1:12.9 | Royal Jewelry Museum, longer elegant shots |
| 1:42–1:45 | quiet break | Glowing doorway dissolves into the harbour lights at night |
| 1:45–2:00 | section hit | Night downtown |
| 2:00–2:17 | build → peak | Next morning: Corniche drive → Stanley Bridge → turquoise bay |
| 2:17–2:34 | outro | Bay → golden-hour locomotive → the sea, "until we meet again" |

Hard cuts land on beats, and all 44 were verified frame-exact by scene detection. There are 6
dissolves in all, used only in calm passages: two in the intro, plus museum → night,
night → morning, and two in the outro. The film has no speed ramps and no artificial zooms.

## Image

- Tone mapping is HLG → Rec.709 with the hable curve at 100-nit reference. It was chosen over
  mobius and reinhard after side-by-side tests, because it keeps highlight detail in skies and
  bright doorways and keeps the natural iPhone look.
- On top of that there is only a global +3% contrast and +4% saturation, with no per-shot looks
  and no sharpening.
- There is no stabilization. Every clip was measured with vidstab; the iPhone footage is already
  steady, and stabilizing would have cropped and softened it.
- Titles use Cormorant Garamond (the wordmark and the italic) and Inter Light (the subtitle),
  with a slow fade-in and the letter-spacing easing in. They sit only on open sky.

## Rebuilding

`tools/edl.py` is the edit decision list. Run the steps in order:

1. `shots.py sdr|hdr` renders each shot.
2. `titles.py <dir> sdr|hdr` renders the titles.
3. `audio.py` builds the song edit and the mix.
4. `assemble.py <dir> sdr|hdr` assembles the master.

The scripts expect the source clips in `src/vid/` and the song in `audio/song.wav`, under the
working directory.
