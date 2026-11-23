# Inside the Motor: Induction vs. Synchronous

A 36-slide briefing built on the official PDO corporate PowerPoint template. It introduces electric motors to people with no electrical background, and the difference between induction and synchronous motors in particular.

- **4.69 MB**, small enough for Outlook. The previous version was 49.8 MB.
- **No video, no GIF and no 3D-model objects.** All motion is native PowerPoint: Morph transitions, spin, fade and motion-path animations.
- **About 12 min 40 s** to present, including all animations and transitions.

## Files

| File | What it is |
|---|---|
| `Inside_the_Motor_Induction_vs_Synchronous.pptx` | **The presentation.** Fully editable, on the PDO master template, with timed speaker notes on every slide. |
| `images/parts/` | The 3D renders of every motor part, the source images for the Construction section. |
| `models3d/` | Scene data used for the layout, plus the .glb models of each part (not embedded in the deck). |
| `video/` | The earlier MP4 animations. They are **not** used in the deck any more and are kept only as an archive. |
| `viewer/motor_explorer_offline.html` | An optional interactive 3D model for Q&A that opens offline in any browser. |
| `source/` | Everything needed to rebuild the deck (see [Rebuilding](#rebuilding)). |

## Story and timing

| # | Slide | Time |
|---|---|---|
| 1 | Cover | 0:25 |
| 2 | **What does an electric motor do?** Electricity → magnetism → rotation, animated | 0:40 |
| 3 | Two motor families, one key difference. Live speed dials (native spin) | 0:40 |
| 4 | Section: Construction | 0:06 |
| 5 | Two main parts: stator and rotor | 0:30 |
| 6–7 | Induction motor, the complete machine: it turns slowly into view (automatic Morph) | 0:17 |
| 8–9 | It opens up: the covers lift away (automatic), then the parts slide apart into a numbered exploded view | 0:22 |
| 10–16 | Induction components, one per slide: 1 Stator · 2 Rotor · 3 Rotor bars and end rings · 4 Shaft · 5 Bearings · 6 Frame / housing · 7 Cooling fan | 1:33 |
| 17–18 | Synchronous motor, the complete machine: turn (automatic) | 0:17 |
| 19–20 | It opens up into a numbered exploded view | 0:22 |
| 21–27 | Synchronous components: 1 Stator · 2 Rotor with poles · 3 Field coils · 4 Damper bars · 5 Slip rings and brushes · 6 Excitation system · 7 Frame and cooling | 1:40 |
| 28 | Section: How they work | 0:06 |
| 29 | **The rotating magnetic field**, native animation | 0:50 |
| 30 | **Induction motor: how it turns**, native animation | 1:00 |
| 31 | **Synchronous motor: how it locks in step**, native animation | 1:00 |
| 32 | The fundamental difference: rotor magnetism, slip, speed | 0:50 |
| 33 | Strengths and limitations | 0:45 |
| 34 | Where we use each motor | 0:40 |
| 35 | What should we remember? | 0:30 |
| 36 | Thank you | 0:05 |
| | **Total** | **12:38** |

Slides 6, 8, 17 and 19 advance by themselves after a fraction of a second, so each motor turns and opens up in one smooth move. The presenter clicks 30 times in all.

### Content changes from the previous version

- **Removed:** the rotor-design and excitation slide, which was too detailed, and the 11-row comparison table, whose essentials are already on "The fundamental difference" and "Strengths and limitations".
- **Simplified:** the synchronous motor now has 7 parts instead of 10. Its shaft, bearings and frame do the same job as in the induction motor, so they are merged into "Frame and cooling".
- **Plainer English throughout:** for example "rotor magnetism" instead of "rotor excitation", and "draws extra magnetising current" instead of "lagging power factor".
- **Added:** "What does an electric motor do?", and a turn-and-open-up sequence for each motor.

## How the motion works (all native PowerPoint)

### Construction: 3D renders moved by Morph

- **Realistic parts.** Every part is a realistic 3D render, a transparent picture with the same name on every slide (for example `!!induction_rotorAsm`). All the slides are views from one virtual camera, so Morph moves the parts the way a camera would:
  - **Turn:** the complete motor turns slowly, a Morph between two renders 16° apart.
  - **Opening up:** the covers lift away, then the parts slide apart into the exploded view.
  - **Focus:** the selected part grows to the centre while the others fly out past the slide edges.
  - **Part to part:** the scene pans, and the next part arrives from its real direction in the motor with a gentle ±9° turn.
- **Revealed after each move.** A leader line draws from the part to its number, then the name and explanation fade in. A ring on the "where it sits" map moves to the part.
- **Limitation.** A picture cannot rotate freely in 3D. Genuine PowerPoint 3D-model objects could, but the hand-built version would not open on PowerPoint for iPhone, so this deck does not use them. The turning effect comes from Morph between renders taken from different angles.

### Working principle: shapes animated with spin, fade and motion paths

| Slide | What the audience sees |
|---|---|
| Rotating magnetic field | Three coil pairs light up one after another. A North–South field appears and turns. A compass needle appears and follows it. |
| Induction motor | The field turns. Currents appear in the rotor bars under the poles. Torque arrows appear. The rotor speeds up and then keeps turning slightly slower than the field (slip, exaggerated so it can be seen). |
| Synchronous motor | The field turns. The rotor is spun up, as by its damper bars. DC is switched on (glow). The rotor locks in step and turns at exactly the field speed, trailing by a small angle. |
| Two motor families | Two speed dials: on the induction dial the rotor hand falls behind, on the synchronous dial it stays with the field hand. |
| What a motor does | An energy pulse travels from the electricity symbol to the motor, then to a spinning fan. |

Each of these slides runs by itself from the moment it appears. The speaker notes give the narration that goes with it. Parts that must stay in step, such as the synchronous rotor locking onto the field, are started on exact multiples of the field's revolution time (4 s), so they stay aligned.

## File size

| | Before | After |
|---|---|---|
| File size | 49,847,668 bytes (49.8 MB) | **4,918,239 bytes (4.69 MB)**: 90.1 % smaller |
| Videos (MP4) | 25.8 MB | none |
| GIF | 0.8 MB | none |
| 3D renders (PNG) | 20.2 MB | 4.4 MB |
| Photos (JPEG) | 2.9 MB | 0.25 MB |

How the reduction was achieved:

- **Videos and the GIF removed**, replaced by native animation.
- **Every picture sized to its on-screen size** at 165 pixels per inch, about 1.15 × a 1920-pixel projector. Before, renders were up to 1,700 px for small areas.
- **Transparent margins cropped** from every render.
- **3D renders compressed with libimagequant**, the palette quantizer behind pngquant and TinyPNG. Transparency is kept, and the renders are visually indistinguishable from the originals at 2× zoom.
- **Photos re-encoded** as progressive JPEG at quality 84, at their displayed size.
- **Unused material dropped:** the old component stills and media are gone. The SharePoint library metadata inherited from the intranet template is removed, and the document properties are regenerated.

## Verification report

### Checks completed

| Check | Result |
|---|---|
| Opens and is a genuine PowerPoint package | Validation against the PDO template passed. The zip is intact, `[Content_Types].xml` is first, and every relationship resolves. Reopened with python-pptx (36 slides). LibreOffice opens it, renders all 36 slides and saves it back to .pptx. |
| Fully editable | No password, "Final" mark, write-protection or library binding. All text is live text, and all diagrams are editable shapes. |
| No embedded video | No MP4, GIF, 3D-model or other media parts at all. |
| Animations | 207 animation effects on 9 slides. Every target shape exists, timing node IDs are unique, and every spinning group is exactly centred on its pivot (checked numerically), so nothing wobbles. The load-angle and dial-lag rotations are written correctly. |
| Morph | 20 Morph transitions, each with a fade fallback. Every part keeps its name from slide to slide (9–13 parts carried over per move). |
| Auto-advance | Slides 6, 8, 17 and 19 advance after 0.6 s or 0.15 s. |
| Layout | All 36 slides were rendered and inspected. Overlaps found along the way were fixed. |
| Duration | 12:38 scripted, including animations and transitions. All the native animations finish inside their slide's time (about 25–30 s each). |
| Size | 4.69 MB, comfortably under common Outlook limits (often 10–25 MB, and Base64 encoding in e-mail adds about a third). |

### Compatibility and what could not be tested here

- **Elements used.** The deck uses only standard PowerPoint elements: pictures, shapes, text, Morph and the fade, spin and motion-path effects. All are supported by PowerPoint for Windows, Mac, iPhone/iPad and the web.
- **Morph versions.** Morph needs PowerPoint 2019, 2021 or Microsoft 365. Older versions show a fade.
- **Not tested.** There is no Microsoft PowerPoint in this build environment, so actual playback in PowerPoint for Windows and iPhone could not be tested. **Please click through the deck once in Slide Show on the presenting PC and on the iPhone**, in particular slides 2–3, 6–27 and 29–31.

## Rebuilding

Needs Node with Playwright and headless Chromium, and Python 3 with python-pptx, Pillow and `imagequant`.

| Script | Purpose |
|---|---|
| `motors.js`, `stage.html`, `stage.js` | Procedural three.js models of both motors and the studio renderer |
| `glb.js`, `native_cfg.js` | Export the parts and record the scene data (`models3d/`) |
| `native_layout2.py`, `cfg_v3.py` | Single-camera layout: places every part on every Construction slide, and writes the render list |
| `partimg.js` | Renders each part, and the complete motors, through the layout's camera |
| `anim_native.py` | Native animation toolkit: timeline (fade, spin, motion path) and diagram helpers |
| `build_v3.py`, `v3_head.py`, `notes_v3.py` | The deck builder and the timed speaker notes. Run `python3 build_v3.py raw.pptx`. |
| `fix_package.py` | Final package clean-up. Run `python3 fix_package.py raw.pptx Inside_the_Motor_Induction_vs_Synchronous.pptx`. |

Photo credits (Wikimedia Commons) are printed on the slide: B. S. Janse (CC BY 2.5), Kecko (CC BY 2.0), Asurnipal (CC BY-SA 4.0), L. Lenz (CC BY-SA 4.0), A. van Beem (CC0), V. Bukharov (CC BY-SA 4.0), Jb957 (CC0), J. Knauer (CC BY 3.0), Mriya (CC BY-SA 3.0). The ≈ 45 % electricity figure is from IEA (2011).
