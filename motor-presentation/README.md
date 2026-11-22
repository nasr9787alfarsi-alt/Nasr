# Inside the Motor: Induction vs. Synchronous

A 34-slide technical briefing (plus 2 hidden backup slides) built on the official PDO corporate PowerPoint template. It explains induction and synchronous motors to people without an electrical background, using 3D exploded-view videos, magnetic-field animations, real industrial photos and timed speaker notes on every slide.

**Presentation time: 13 min 41 s, including all video playback** (see [Timing](#timing)).

The Construction section shows each motor as a numbered overview, then **one slide per component**. Each component slide has a large isolated 3D close-up, the same number as in the overview, a name, a one-line explanation and a "where it sits" mini-map. PowerPoint's Morph transition zooms from the overview into each part.

## What's in this folder

| File | What it is |
|---|---|
| `Inside_the_Motor_Induction_vs_Synchronous.pptx` | **The presentation (84 MB).** Editable PowerPoint on the PDO master template. All five videos are embedded inside the file, not linked, so it plays on any computer. Every slide has timed speaker notes. |
| `video/induction_motor_exploded.mp4` | Backup (hidden slide 35). 49 s 3D tour of a squirrel-cage induction motor: it opens up, labels and explains 12 components one by one, then reassembles. 1600×900. |
| `video/synchronous_motor_exploded.mp4` | Backup (hidden slide 36). The same 49 s tour for a large salient-pole synchronous motor with DC excitation. 1600×900. |
| `video/anim_rmf.mp4` | 30 s: how three-phase currents create a rotating magnetic field. 1920×1080. |
| `video/anim_induction.mp4` | 51 s: the induction principle in 8 steps, ending with slip. 1920×1080. |
| `video/anim_sync.mp4` | 49 s: the synchronous principle in 7 steps: damper start, DC excitation, pull-in, lock-in, load angle. 1920×1080. |
| `viewer/motor_explorer_offline.html` | Optional interactive 3D model for Q&A. Opens offline in any browser: rotate, explode or cut away either motor and click a part. |
| `images/components/` | The component renders: a numbered overview for each motor (`*_overview_crop.png` with label positions in `*_overview.json`) and an isolated close-up of every component (`induction_c1–7.png`, `sync_c1–10.png`). The close-ups are 2000×1500 with transparent backgrounds. |
| `images/` | Other high-resolution renders, video posters and the speed-dial GIF used in the deck. |
| `source/` | Everything that generates the assets and the deck (see [Rebuilding](#rebuilding)). |

## Running order and timing

| # | Slide | Time |
|---|---|---|
| 1 | Cover | 0:30 |
| 2 | Two motor families, one key difference | 0:55 |
| 3 | Section: Construction | 0:10 |
| 4 | Two main parts: stator and rotor | 0:30 |
| 5 | **Induction motor: overview with numbered components** | 0:25 |
| 6–12 | **Induction components, one per slide:** 1 Stator · 2 Rotor · 3 Rotor bars and end rings · 4 Shaft · 5 Bearings · 6 Frame / housing · 7 Cooling fan | 1:36 |
| 13 | **Synchronous motor: overview with numbered components** | 0:25 |
| 14–23 | **Synchronous components, one per slide:** 1 Stator · 2 Salient-pole rotor · 3 Field winding · 4 Damper (starting) bars · 5 Slip rings and brushes · 6 DC excitation system · 7 Shaft · 8 Bearings · 9 Frame / housing · 10 Cooling system | 2:00 |
| 24 | The synchronous rotor: design and excitation | 0:35 |
| 25 | Section: How they work | 0:10 |
| 26 | The rotating magnetic field (video, 30 s) | 0:40 |
| 27 | Induction motor: how it turns (video, 51 s) | 1:00 |
| 28 | Synchronous motor: how it locks in step (video, 49 s) | 1:00 |
| 29 | Strengths and limitations | 0:55 |
| 30 | Where we use each motor | 0:50 |
| 31 | The fundamental difference: excitation, slip, speed | 0:55 |
| 32 | Induction vs. synchronous at a glance | 0:25 |
| 33 | What should we remember? | 0:35 |
| 34 | Thank you | 0:05 |
| | **Total** | **13:41** |
| 35–36 | *Hidden backup:* full exploded-view videos of both motors, for Q&A | not timed |

### Timing

- **Component slides are quick.** Each takes 7–20 s: say the number, the name and one sentence. The individual times are in the speaker notes.
- **Narration runs over the videos.** Each video slide's time covers its whole video plus a short introduction.
- **There is spare time.** The total leaves 1 min 19 s before the 15-minute limit. The two exploded-view videos are on hidden slides and don't count toward the time. To show one, jump to slide 35 or 36 during Q&A, for example by typing the slide number and pressing Enter in Slide Show.

### Construction section design

- **Same model, consistent numbers.** Every close-up is rendered from the same 3D model as the overview, with the part isolated and re-framed to fill the panel. Nothing is cropped from the overview. Each number is the same on the overview, the component slide and the mini-map.
- **Morph transitions.** Going from the overview to component 1, the whole motor shrinks into the corner mini-map and the number flies into the large badge. Between components, the green ring on the mini-map moves to the next part. Morph needs PowerPoint 2019, 2021 or Microsoft 365; older versions show a fade instead.
- **See-through parts are labelled.** Where steel is shown transparent or removed to reveal a part (the cage, field winding, damper bars and cooling system), the slide says so.

## Presenting

- Click a video to play it, and click again to pause. Pausing on any component in the exploded views is a good moment for discussion.
- The speed-dial GIF on slide 2 loops automatically.
- Each slide's notes start with `[Time: m:ss · running total m:ss]` so you can keep pace.

## Verification report

### Checks completed

| Check | Result |
|---|---|
| Package validation against the PDO template (schema, relationships, content types) | Passed |
| Videos embedded rather than linked | 5 videos and 1 GIF are inside the file. There are 0 external relationships and 0 references to local file paths. |
| Embedded videos are the final renders, not placeholders | Each embedded mp4 is byte-identical (SHA-1) to the files in `video/`. |
| Construction section | 17 Morph transitions and 2 hidden backup slides are present. All component numbers match the overview. |
| Video format | H.264 High profile, level 4.1, yuv420p, with the index at the start of the file (fast start). This is the format PowerPoint plays natively on Windows and Mac. |
| Video integrity | Every embedded video decodes completely with no errors. |
| Playback wiring | Slides 26, 27, 28 and hidden backups 35 and 36 each have a video, a poster frame, click-to-play timing and a transition. |
| Portability | The deck was copied alone into an empty folder and checked there. |
| Rendering | The deck was opened and rendered in LibreOffice. All 34 visible slides were inspected one by one for overlap, clipping and readability. |
| Video content | Frames were sampled across both exploded videos: assembled view, labelled exploded overview, component highlights and reassembly. |
| Timing | 13:41 scripted, including video playback. |

### Not tested in Microsoft PowerPoint

These checks need Microsoft PowerPoint, which can't run in this build environment:

- Actual video playback inside PowerPoint on Windows or Mac.
- Exact font rendering. The template uses Segoe UI, and the previews used a substitute font.
- Slide-show behaviour: click-to-play, fade and Morph transitions, and the looping GIF. LibreOffice can't play Morph.

**Recommendation:** do one full rehearsal on the presenting computer in Slide Show mode, and play every video once. If a video doesn't play, use *File → Info → Optimize Media Compatibility* in PowerPoint.

## Technical notes

- **Speeds:** synchronous speed = 120 × f ÷ poles. At 50 Hz that's 1500 rpm for a 4-pole motor. A typical full-load induction rotor turns at about 1470 rpm, which is 2 % slip.
- **Exaggerated slip:** the slip in the animations is deliberately larger than in a real motor so you can see it. Every place it appears says so.
- **Real physics:** a simple physics model drives the animations. The induction motor follows a Kloss torque–slip curve. The synchronous motor's torque is proportional to sin δ, plus damper torque.
- **Brush gear model:** the slip-ring brush gear was rebuilt in more detail for the component close-up. The two backup exploded-view videos were rendered before that change, so they show the simpler version.
- **Statistic:** the ≈ 45 % figure for electricity used by motor systems comes from IEA (2011), which estimates 43–46 %.
- **Industrial photos:** from Wikimedia Commons. Each photo's author and licence is printed on the slide.

| Photo | Author | Licence |
|---|---|---|
| Pump | Bernard S. Janse | CC BY 2.5 |
| Tunnel ventilation fan | Kecko | CC BY 2.0 |
| Screw compressor | Asurnipal | CC BY-SA 4.0 |
| Conveyor | Leonhard Lenz | CC BY-SA 4.0 |
| HVAC unit | Alf van Beem | CC0 |
| Mill | Vyacheslav Bukharov | CC BY-SA 4.0 |
| Cement kiln | Jb957 | CC0 |
| Hot strip mill | Jason Knauer | CC BY 3.0 |
| Synchronous condenser | Mriya | CC BY-SA 3.0 |

## Rebuilding

The tools are Node with Playwright and headless Chromium, ffmpeg, and Python 3 with python-pptx and Pillow.

| Script | What it builds |
|---|---|
| `motors.js` | The procedural three.js models of both motors |
| `stage.html`, `stage.js` | The studio scene and labels |
| `director.js` | The exploded-view camera and timing script |
| `video.js` | Renders the exploded-view videos. Run `DPR=0.8334 NO_BUMP=1 node video.js induction out.mp4 20`. |
| `anim.html`, `anim.js`, `animrender.js` | The 2D working-principle animations and the speed-dial GIF |
| `still.js`, `stills_l.sh` | The still renders |
| `build_brand.py` | The deck, built on the PDO template. It reads the assets from `../deliver2/` and the template from `../tpl/template.pptx`. |
| `comp.js` | Renders the numbered overviews and every component close-up. Run `node comp.js induction ../deliver2/comp all 1`. |
| `components_section.py` | Builds the overview and component slides, including Morph. `build_brand.py` loads it. |
| `finalize.sh` | Extracts the posters, then builds and validates the deck |
| `verify.py` | Checks embedding and decodes every video |
| `viewer.js`, `viewer_tpl.html` | The offline 3D explorer |

`three.min.js` (r128), `RoomEnvironment.js` and `BufferGeometryUtils.js` are vendored copies of three.js (MIT).
