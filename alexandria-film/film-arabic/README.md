# الإسكندرية: rebuilt film (49.4 s)

This is a fresh edit, rebuilt from a new review of all 75 clips. It has 24 shots, and no subject,
angle or location repeats. The grade is the same natural one as the full film.

## Structure

The music is one continuous section of the song, from the section hit at 4:24.1 to its natural
ending, with no edits.

| Film | Chapter | Shots |
|---|---|---|
| 0–3.6 s | Departure | the traveller watching the train, golden fields through the window |
| 3.6–10.2 s | Arrival | the Mediterranean (the first sight of the city), the square, a taxi, a narrow street, a woman walking |
| 10.2–19.9 s | Royal Jewelry Museum | the palace exterior (held), the red staircase on the big accent, the chandelier hall, the queen's portrait, the jewels, the glowing doorway held for 3 s |
| 19.9–23.5 s | Night, at the song's loudest | light beams over the crowd, evening crowds, the long night street |
| 23.5–31.3 s | The Corniche | Stanley Bridge, a red car along the railing, the view from above, the sea and the pier |
| 31.3–40.0 s | Golden hour, as the song resolves | the turquoise bay (dissolve), the old locomotive (dissolve), flags in the last light |
| 40.0 s | Ending | the sea, on the final strong beat |

- Every hard cut is on a beat and was confirmed frame-exact.
- The only transitions are two 0.6 s dissolves, used where the song settles.

## Ending

- **Last note.** It rings at 45.4 s, while the sea fades to black over 2 s.
- **Music fade.** The music then fades with a smooth curve from 45.9 s to complete silence at
  49.4 s (−115 dB at the last frame), so nothing is cut off.
- **Sound under the picture.** The sound of the sea sits under the final shot.

## Arabic title

- **Text and font.** "الإسكندرية" in Aref Ruqaa (Ruqʿah calligraphy) at 50 px, between two thin
  hairlines, with a soft shadow.
- **Size and position.** About 300 px wide, centred about 120 px above the bottom edge.
- **Rendering.** `tools/title_ar.js` renders it with Chromium's Arabic shaping, so the letters
  join and run right to left. It writes a transparent PNG, saved here as `title_ar.png`.
- **Timing.** It is overlaid above the picture fades, so it is visible on every frame from the
  first to the last.
- **Font file.** Aref Ruqaa comes from the `@fontsource/aref-ruqaa` npm package. Put it in
  `fonts_ar/`.

## Building it

Use the full film's tools, but take `edl.py`, `audio50.py` and `assemble50.py` from here, and put
`beatmap.txt` and `splices.json` in `audio/`. Then run:

1. `node title_ar.js <dir>`
2. `shots.py sdr`
3. `audio50.py`
4. `assemble50.py <dir>`
