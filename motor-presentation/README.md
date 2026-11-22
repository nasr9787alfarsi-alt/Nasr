# Inside the Motor: Induction vs. Synchronous

A 34-slide technical briefing built on the official PDO corporate PowerPoint template. It explains induction and synchronous motors to people without an electrical background, using high-quality 3D renders with PowerPoint Morph transitions, magnetic-field animations, real industrial photos and timed speaker notes on every slide.

**Presentation time: 13 min 41 s, including all video playback** (see [Timing](#timing)).

**The Construction section uses no video.** Every motor part is a separate high-quality 3D render, placed by a single-camera layout. PowerPoint's own Morph transition moves the parts between slides the way the camera moves in the reference video. Each motor starts with an exploded overview with numbered parts, then gives **each component its own slide**: the part enlarged on its own, with the same number, its name, a one-line explanation and a "where it sits" mini-map.

> **Compatibility fix (iPhone).** An earlier build embedded each part as a hand-authored PowerPoint 3D-model object (`am3d:model3d`, .glb). PowerPoint for iPhone could not open that file. The corrected deck uses standard picture objects in the same positions, with the same Morph moves. It contains only markup that PowerPoint writes itself, and its package metadata has been cleaned (see the verification report below). The 3D-model build is kept, clearly labelled, as `EXPERIMENTAL_3D_models_untested.pptx`.

## What's in this folder

| File | What it is |
|---|---|
| `Inside_the_Motor_Induction_vs_Synchronous.pptx` | **The presentation (50 MB). Use this one.** Editable PowerPoint on the PDO master template, for desktop PowerPoint and PowerPoint for iPhone and iPad. Construction parts are high-quality 3D renders moved by Morph. The three working-principle animations (slides 26–28) are embedded H.264 videos. Every slide has timed speaker notes. |
| `EXPERIMENTAL_3D_models_untested.pptx` | The same deck with each Construction part as a hand-authored PowerPoint 3D model. It is **not** for presenting: PowerPoint for iPhone could not open it, and it has never been opened in desktop PowerPoint. Kept only for experiments. |
| `models3d/` | The 25 motor parts as .glb 3D models, used only by the experimental deck (glTF 2.0, validated with the Khronos glTF validator), plus the layout data. |
| `video/induction_motor_exploded.mp4` | Not used in the deck. 49 s 3D tour of a squirrel-cage induction motor: it opens up, labels and explains 12 components one by one, then reassembles. 1600×900. |
| `video/synchronous_motor_exploded.mp4` | Not used in the deck. The same 49 s tour for a large salient-pole synchronous motor with DC excitation. 1600×900. |
| `video/anim_rmf.mp4` | 30 s: how three-phase currents create a rotating magnetic field. 1920×1080. |
| `video/anim_induction.mp4` | 51 s: the induction principle in 8 steps, ending with slip. 1920×1080. |
| `video/anim_sync.mp4` | 49 s: the synchronous principle in 7 steps: damper start, DC excitation, pull-in, lock-in, load angle. 1920×1080. |
| `viewer/motor_explorer_offline.html` | Optional interactive 3D model for Q&A. Opens offline in any browser: rotate, explode or cut away either motor and click a part. |
| `images/parts/` | Transparent renders of every part through the same camera as its 3D model. They are the 3D models' preview and fallback pictures, and the backup deck's pictures. |
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

### Timing

- **Component slides are quick.** Each takes 7–20 s: say the number, the name and one sentence. The individual times are in the speaker notes.
- **Narration runs over the videos.** The three working-principle videos (30 s, 51 s and 49 s) each fit inside their slide's time.
- **There is spare time.** The total leaves 1 min 19 s before the 15-minute limit.

### Construction section design: Morph camera moves

The camera technique follows the reference video. One continuous model is never cut; the view moves smoothly from the whole motor to each part.

- **One camera for every slide.** Each Construction slide is a view of the same virtual camera on the exploded motor. Every part is a separate transparent render with the same name on every slide (`!!induction_frame`, `!!sync_rotorAsm` and so on), so Morph moves each part exactly as a camera move would.
  - **Overview to a part:** the selected part grows to the centre while the others fly out past the slide edges.
  - **Part to part:** the scene pans. The old part leaves, and the next arrives from its true direction relative to it, turning gently (±9°).
  - **Moving parts:** on the frame slide the end shields glide onto the frame, and on the cooling slide the shaft fan moves under the cooler.
- **Revealed after each move.** A leader line wipes in from the part to its number, then the name and explanation fade in. The ring on the "where it sits" mini-map moves to the new part.
- **Version support.** Morph plays in PowerPoint 2019, 2021, Microsoft 365, PowerPoint for Mac, PowerPoint for iPhone and iPad, and PowerPoint for the web. Older versions show a fade instead.
- **Parts removed to show others are labelled.** Where steel is removed to reveal a part (the cage, field coils and damper bars), the slide says so.

## Presenting

- Click a video to play it, and click again to pause. Pausing on any component in the exploded views is a good moment for discussion.
- The speed-dial GIF on slide 2 loops automatically.
- Each slide's notes start with `[Time: m:ss · running total m:ss]` so you can keep pace.

## Verification report

### iPhone "couldn't open" and read-only: what happened and what was fixed

| Finding | Detail | Fix |
|---|---|---|
| **Hand-authored 3D-model objects (most likely cause)** | The previous build contained 193 PowerPoint 3D-model placements (`am3d:model3d`) and 25 .glb models. This was the only markup in that file that PowerPoint had never written itself. Its camera, viewport and light values were inferred from the schema, because no PowerPoint-written sample was reachable from this environment. PowerPoint apps that support 3D models read this markup instead of the fallback picture. Desktop can sometimes repair a file, but the mobile apps refuse to open it. | Each part is now a standard picture of the same render, in the same position and with the same name, so the Morph moves are unchanged. The corrected file contains no `am3d` markup. |
| Stale document properties | `docProps/app.xml` still described the original 24-slide template: 0 notes, 0 media clips and an outdated slide-title list. | Regenerated from the real content: 34 slides, 34 notes pages, 0 hidden slides, 3 media clips. |
| SharePoint library binding from the PDO intranet template | The template carried a SharePoint document-library content type, document-management properties and form templates (`customXml/*`, the `ContentTypeId` custom property). Office treats such files as belonging to a server library, which can make them open read-only outside that library. | Removed (10 parts). The design, theme, layouts and branding are untouched. |
| Read-only on iPhone | PowerPoint for iPhone opens files received from another app (Mail, Messages, Files preview, a chat app) read-only, as a protected copy. It also falls back to read-only when it cannot fully load a file. | The file is no longer write-protected in any way: there is no modify password, "Final" status or library binding. To edit on the iPhone, tap **Edit** or **Save a Copy** (or Duplicate). That saves your own editable copy. |

### Checks completed on the corrected file

| Check | Result |
|---|---|
| Real PowerPoint package, not a renamed file | Zip header and MIME detection give "Microsoft PowerPoint 2007+". `[Content_Types].xml` is the first entry. |
| Zip integrity | The test passed, with no duplicate entries and every part deflated. |
| XML | All parts parse. Every relationship target exists. Every part has a content type. No overrides point at missing parts. |
| Schema validation against the PDO template | Passed |
| Slide structure | Child elements are in schema order on all 34 slides. Shape IDs are unique on every slide. |
| Element inventory | Pictures, shapes, text, one table, Morph (17 slides, each with a fade fallback), fades, entrance animations (19 slides) and 3 embedded videos (slides 26–28). There are no 3D-model objects, OLE, ActiveX or ink. |
| Independent reader | Reopened with python-pptx: all 34 slides load. |
| LibreOffice | The deck opens and renders all 34 pages, and saves back to .pptx successfully. All slides were inspected. |
| Timing | 13:41 scripted, including video playback. |

### Not tested in Microsoft PowerPoint

There is no PowerPoint, desktop or iPhone, in this build environment, so these could not be tested: opening the file in PowerPoint itself, Morph playback, and video playback. Please open the corrected file once on the iPhone and once on the presenting PC, and click through slides 5–23 and 26–28 in Slide Show.

## Technical notes

- **Speeds:** synchronous speed = 120 × f ÷ poles. At 50 Hz that's 1500 rpm for a 4-pole motor. A typical full-load induction rotor turns at about 1470 rpm, which is 2 % slip.
- **Exaggerated slip:** the slip in the animations is deliberately larger than in a real motor so you can see it. Every place it appears says so.
- **Real physics:** a simple physics model drives the animations. The induction motor follows a Kloss torque–slip curve. The synchronous motor's torque is proportional to sin δ, plus damper torque.
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
| `native_cfg.js` | Which parts form each 3D object, the overview set and the components, plus the shared view direction. |
| `glb.js` | Exports each part as a .glb 3D model, re-centred and pre-rotated to the overview view. Run `node glb.js induction ../deliver2/native`. |
| `native_layout.py` | The single-camera layout engine: places every part on every Construction slide. Running it writes the render job list. |
| `partimg.js` | Renders each part's picture through the same camera as its 3D model. |
| `components_section.py` | Builds the Construction slides as pictures (`NATIVE_MODE=img`, used for the presentation) or experimental 3D models (`NATIVE_MODE=3d`), with Morph and the reveal animations. |
| `fix_package.py` | Final package clean-up: regenerates the document properties and removes the inherited SharePoint library binding. Run `python3 fix_package.py built.pptx final.pptx`. |
| `film.js` | Renders the overview still and label positions used for the "where it sits" mini-map. |
| `finalize.sh` | Extracts the posters, then builds and validates the deck |
| `verify.py` | Checks embedding and decodes every video |
| `viewer.js`, `viewer_tpl.html` | The offline 3D explorer |

`three.min.js` (r128), `RoomEnvironment.js` and `BufferGeometryUtils.js` are vendored copies of three.js (MIT).
