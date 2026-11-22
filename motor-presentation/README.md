# Inside the Motor: Induction vs. Synchronous

A 17-slide technical briefing that takes about 15 minutes to present. It's built on the official PDO corporate PowerPoint template and explains induction and synchronous motors to people without an electrical background. It uses 3D exploded-view videos, magnetic-field animations, real industrial photos and speaker notes on every slide.

## What's in this folder

| File | What it is |
|---|---|
| `Inside_the_Motor_Induction_vs_Synchronous.pptx` | **The main deliverable.** An editable PowerPoint built on the PDO master template, so the logos, colours, Segoe UI fonts and layouts are all the template's own. Every video is embedded, every slide fades in, and every slide has speaker notes. |
| `video/induction_motor_exploded.mp4` | A 45 s 3D tour of a squirrel-cage induction motor. It opens up step by step, highlights and explains 12 components, then reassembles. |
| `video/synchronous_motor_exploded.mp4` | The same 45 s tour for a large salient-pole synchronous motor. |
| `video/anim_rmf.mp4` | A 30 s animation showing how three-phase currents create a rotating magnetic field. |
| `video/anim_induction.mp4` | A 51 s animation of the induction motor working principle in 8 steps: the rotating field, induced bar currents, the rotor's own poles, torque, acceleration and slip. |
| `video/anim_sync.mp4` | A 49 s animation of the synchronous motor in 7 steps: why it can't start by itself, damper start, DC excitation, pull-in, lock and load angle. |
| `viewer/motor_explorer_offline.html` | An optional interactive 3D model for Q&A. Open it in any browser, offline, to rotate, explode or cut away either motor and click a part to see what it does. |
| `images/` | High-resolution renders with transparent backgrounds, plus the speed-comparison GIF. |
| `source/` | The scripts that generate everything: the 3D models (three.js), the animations (Canvas 2D), the video rendering and the deck (`build_brand.py`, using python-pptx on the template). |

## Running order (about 15 minutes)

| # | Slide | Layout |
|---|---|---|
| 1 | Cover | Cover 3 |
| 2 | Two motor families, one key difference | Split screen with live speed dials |
| 3 | Section: Construction | Section, with a cutaway render |
| 4 | Stator and rotor | Large central render |
| 5 | Induction motor exploded view | Video |
| 6 | Squirrel-cage rotor | |
| 7 | Synchronous motor exploded view | Video |
| 8 | Rotor designs and excitation | |
| 9 | Section: How they work | Section |
| 10 | Rotating magnetic field | Video |
| 11 | Induction working principle and slip | Video |
| 12 | Synchronous working principle and starting methods | Video |
| 13 | Strengths and limitations, including power factor | |
| 14 | Applications | Photographs |
| 15 | Comparison table | |
| 16 | What to remember | |
| 17 | Thank you | |

## Presenting

- **Videos:** click a video to play it, and click again to pause. Each one is narrated step by step in that slide's speaker notes.
- **Speed dials:** the GIF on slide 2 loops automatically.

## Technical notes

- **Speeds:** synchronous speed = 120 × f ÷ poles. At 50 Hz that's 1500 rpm for a 4-pole motor. A typical full-load rotor speed is about 1470 rpm, which is 2 % slip.
- **Exaggerated slip:** the slip in the animations is deliberately larger than in a real motor so you can see it. Every place it appears says so.
- **Real physics:** a simple physics model drives the animations. The induction motor follows a Kloss torque–slip curve. The synchronous motor's torque is proportional to sin δ, plus damper torque. So the rotor speeds up, pulls in and settles at a load angle realistically rather than being keyframed.
- **Industrial photos:** all from Wikimedia Commons. Each photo's author and licence is printed on the slide.

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

- **Statistic:** the ≈ 45 % figure for electricity used by motor systems comes from IEA (2011), which estimates 43–46 %.
