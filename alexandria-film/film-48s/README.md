# ALEXANDRIA: 48-second film (47.9 s)

This is a separate final version, made from a fresh review of all 75 clips. It has 31 shots, and
the grade and picture treatment are the same as the full film.

## Music: one continuous section, no edits

- **The section.** The film runs from the section hit at 4:24.1 to the song's own ending. That
  covers a build, the big accent at 12.3 s, the loudest stretch of the song (19.9–30 s), the outro
  from 32.4 s and the final note.
- **No joins.** Because the section is continuous, the music is untouched.
- **Timing.** The beat grid is aligned to the measured onset of the opening hit.
- **Loudness.** −13.9 LUFS, with a −1.5 dB peak.

## Structure

| Film | Music | Shots |
|---|---|---|
| 0–3.6 s | section hit | the traveller watching the train, then golden fields through the window |
| 3.6 s | — | Stanley Bridge, with the ALEXANDRIA title |
| 6.1–12.3 s | build | square, taxi, palace with flags, statue, alley, palace facade |
| 12.3 s | accent | staircase, chandelier hall, stained glass and portrait, red jewellery, glowing doorway, corridor |
| 19.9 s | loudest part | night lights and crowds, then the sea, Stanley tower, the Corniche, the railing, the sea and the pier |
| 32.4 s | outro | turquoise bay, flags in golden light, a dissolve to the golden-hour locomotive |
| 40.0 s | final strong beat | the sea, with the ALEXANDRIA signature |

- There is one train shot and one window shot, 3.6 s in total.
- Shots run from 0.5 to 2.5 s, with longer holds only in the outro.
- Every hard cut was confirmed frame-exact.

## Title

- **Text and font.** "ALEXANDRIA" in Cormorant Garamond Light, 46 px, with wide letter-spacing
  that settles as it fades in. It has a 35% soft shadow and appears twice.
- **Opening.** On the Stanley Bridge hero shot, at 86% of the frame height, between the lane lines.
- **Ending.** On the final sea shot, at 81% of the frame height, over calm water. It leaves with the
  picture fade.

## Building it

Use the full film's `tools/`, but replace `edl.py` with the version here. Put `beatmap.txt` and
`splices.json` in `audio/`. Then run:

1. `titles45.py <dir>`
2. `shots.py sdr`
3. `audio45.py`
4. `assemble45.py <dir>`
