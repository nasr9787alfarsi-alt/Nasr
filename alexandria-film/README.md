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

All three are 1080×1920, 30 fps, 2:02. The masters are cut from 10-bit ProRes 422 HQ
intermediates.

**Why vertical and not 4K 16:9:** every source clip is vertical 1080p. A 16:9 frame would mean
either cropping each shot to about a third of its frame and upscaling it about 3.5×, or
pillarboxing on a blurred background. Both throw away the image quality the brief puts first,
so the film keeps the native frame with no upscaling.

## Selection: quality over quantity

37 of the 75 clips are used. An earlier 2:34 cut used 51 clips and was tightened after the
brief asked for quality over quantity. The film drops:

- near-duplicates, such as a second and third high bay view and a second turquoise-bay angle
- dark or blurred shots: the dark station tunnel, the harbour at night as it blurs, and a
  half-lit monument
- filler streets, such as a plain wall, the back of a head and a station exterior
- car-window shots dominated by billboard ads
- museum padding

## Music edit

- Tempo is 117.5 BPM (one beat is 0.511 s).
- The chorus at 49.0 s returns exactly 376 beats later, at 240.3 s.
- The song is spliced on a bar line inside that repetition, 65.27 s → 256.53 s, with a 30 ms
  equal-power crossfade. Similarity stays between 0.984 and 0.988 across ±8 beats, so this is a
  true repeat.
- The result keeps the free intro, the band drop, the first chorus, the section hit, the peak
  and the original outro: 2:00 of music, with the picture fading out as the last note decays.
- The splice sits inside a single held shot (the red-carpet staircase).
- The ~3 dB dip at the splice is in the song itself: it is a phrase ending, and it is identical
  at both points.
- The mix is normalised to −14 LUFS integrated and −1 dBTP.
- Natural sound from the clips is high-passed at 180 Hz to remove wind and kept low under the
  music: the platform, the approaching and passing train, and the sea under the end card.

## Structure (2:02)

| Film time | Music | Picture |
|---|---|---|
| 0:00–0:13 | free intro | Dawn platform → the traveller watching the train → headlight approaching |
| 0:13 | band drop | Train blasts past |
| 0:13–0:49 | verse | Window views → train pulls in → square, taxis, alley |
| 0:49 | chorus hit | Sea reveal with the **ALEXANDRIA** title |
| 0:53–1:13 | chorus | Streets → palaces → Royal Jewelry Museum, ending on a glowing doorway in the musical breath |
| 1:13 | section hit | Night downtown |
| 1:25 | accent | Hard cut to the next morning's sea → Stanley Bridge |
| 1:33–1:45 | peak | Bridge towers, Corniche traffic, the bay from above |
| 1:45–2:02 | outro | Turquoise bay → golden-hour locomotive → the sea, "until we meet again" |

Hard cuts land on beats, and all 32 were verified frame-exact by scene detection. The film has
4 dissolves, two in the intro and two in the outro. It has no speed ramps and no artificial
zooms.

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

## iPhone / WhatsApp / Instagram export

The delivery files are encoded from the untouched ProRes master, with no change to the edit, grade or mix:

```
ffmpeg -i master_sdr.mov -map 0:v:0 -map 0:a:0 \
  -vf scale=out_range=tv:out_color_matrix=bt709,format=yuv420p,setsar=1 \
  -c:v libx264 -preset slow -profile:v high -level:v 4.1 -g 60 -keyint_min 30 -sc_threshold 0 -bf 2 -refs 3 \
  -color_range tv -colorspace bt709 -color_trc bt709 -color_primaries bt709 -r 30 \
  -crf 17 -maxrate 14M -bufsize 28M \
  -c:a aac -b:a 256k -ar 48000 -ac 2 -movflags +faststart -tag:v avc1 \
  Alexandria_Film_iPhone_H264_1080p.mp4
```

| File | Encode | Size |
|---|---|---|
| `Alexandria_Film_iPhone_H264_1080p.mp4` | the command above | 199 MB |
| `Alexandria_Film_Share_H264_1080p.mp4` | `-crf 20 -maxrate 6M -bufsize 12M`, AAC 160k | 92 MB |

Compared with the master, the iPhone file scores SSIM 0.988 / PSNR 44.6 dB and the share file
SSIM 0.979 / PSNR 41.3 dB.

**Checking playback:**

- `tools/playtest.js` plays a file at 1× in Chromium over HTTP and checks:
  - that it reaches `ended`
  - decoded and dropped frames
  - that the whole AAC track decodes
- `tools/rvfc.js` reads the decoded frames during playback, to confirm a real picture throughout.
