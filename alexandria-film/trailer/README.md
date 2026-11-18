# ALEXANDRIA: trailer cut (1:14)

This is a 73.7-second re-edit of the full film, built from the original clips and the song. Nothing
is sped up. It uses 23 shots, and the picture treatment, titles and transitions are the same as
the full film.

## Music: three segments of the original song

| Film | Song | Section |
|---|---|---|
| 0:00–0:26.1 | 0:00–0:26.1 | Free intro, then the band drop at 13.4 s |
| 0:26.1–0:36.8 | 0:42.4–0:53.1 | Rest of the verse, then the chorus hit at film 32.7 s |
| 0:36.8–1:13.7 | 4:36.4–end | Accent, peak, outro and the song's own ending |

- **Splice 1** removes one 32-beat verse cycle. The verse repeats there, so the material matches on
  both sides (similarity 0.980).
- **Splice 2** cuts at the end of a chorus phrase into the strongest accent downbeat in the second
  half of the song (similarity 0.933; the song stays in A throughout). It falls on a hard picture
  cut.
- Both splices use a 30 ms equal-power crossfade. They are click-free, and the level changes across
  them match the song's own (+1.7 dB and +0.7 dB).
- The mix is −14 LUFS with a −1.1 dB peak.

## Structure

| Time | Part | Shots |
|---|---|---|
| 0:00 | Departure | Platform, train nose, the traveller, headlight |
| 0:13 | Drop | Train blasts past, golden fields, viaduct, train pulls in |
| 0:26 | Arrival | Station square, taxi, alley |
| 0:33 | Chorus hit | Sea reveal with the ALEXANDRIA title |
| 0:37 | Accent | Palace, red-carpet staircase, night light beams |
| 0:44 | Peak | Stanley Bridge towers, Stanley tower, the Corniche railing, the sea from above, the Corniche from above |
| 0:57 | Outro | Turquoise bay, golden locomotive, the sea with "until we meet again" |

- All hard cuts are on beats. Scene detection matched every cut it picked up to its planned frame.
- There are four dissolves, in the intro and outro only.

## Building it

Copy `tools/` from the full film and replace `edl.py`, `audio.py` and `assemble.py` with the
versions here. Put `beatmap.txt` and `splices.json` in `audio/`. Then run `shots.py sdr`,
`audio.py` and `assemble.py <dir> sdr`, and encode with the iPhone H.264 settings in the main
README.
