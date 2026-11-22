# Inside the Motor: Induction vs. Synchronous

A 22-slide technical training deck for people who don't have an electrical background. It covers how induction and synchronous motors are built, how they work, where each one is used and how to tell them apart. It uses original 3D models, exploded-view videos, working-principle animations and speaker notes on every slide.

## What's in this folder

| File | What it is |
|---|---|
| `Inside_the_Motor_Induction_vs_Synchronous.pptx` | The editable PowerPoint deck. Every video is embedded and every slide has speaker notes. |
| `video/induction_motor_exploded.mp4` | A 51 s 3D exploded-view tour of a squirrel-cage induction motor, with 12 labelled components. |
| `video/synchronous_motor_exploded.mp4` | A 51 s 3D exploded-view tour of a salient-pole synchronous motor, with 12 labelled components. |
| `video/anim_rmf.mp4` | A 30 s animation showing how three-phase currents create a rotating magnetic field. |
| `video/anim_induction.mp4` | A 51 s animation of the induction motor working principle in 8 steps, including slip. |
| `video/anim_sync.mp4` | A 49 s animation of the synchronous motor in 7 steps: why it can't self-start, damper start, DC excitation, pull-in, lock and load angle. |
| `viewer/motor_explorer_offline.html` | An interactive 3D viewer that works offline. Open it in any browser to rotate, zoom, explode or cut away either motor, and click a part to see what it does. |
| `images/` | High-resolution renders with transparent backgrounds, plus the speed-comparison GIF. |
| `source/` | The scripts that generate the 3D models (three.js), the animations (Canvas 2D), the videos and the deck (pptxgenjs). |

The videos are also embedded in the deck. They're kept here as separate files so they can be played on their own.

## Presenting

- **Videos:** click a video on its slide to play it, and click it again to pause. Each one is narrated step by step in that slide's speaker notes.
- **Speed dials:** the GIF on slide 3 loops automatically.
- **Questions:** for live Q&A, open `viewer/motor_explorer_offline.html` in a browser.
- **Timing:** the deck runs about 35–45 minutes with the videos.

## Slide flow

1. Title
2. Why motors matter
3. The one-sentence difference
4. Stator vs. rotor
5. Induction motor exploded view
6. Squirrel-cage rotor
7. Synchronous motor exploded view
8. Salient-pole vs. cylindrical rotor
9. Excitation: slip rings vs. brushless
10. The rotating magnetic field
11. Induction motor working principle
12. Slip
13. Synchronous motor working principle
14. Starting methods
15. Power factor
16. Induction motor pros and cons
17. Synchronous motor pros and cons
18. Induction motor applications
19. Synchronous motor applications and the synchronous condenser
20. Comparison table
21. What to remember
22. Closing

## Technical notes

- **Speeds:** the figures use a 50 Hz supply. Synchronous speed is 120 × f ÷ poles, which gives 1500 rpm for a 4-pole motor. A typical full-load rotor speed is about 1470 rpm, which is 2 % slip.
- **Exaggerated slip:** the slip in the animations and the speed GIF is deliberately larger than in a real motor so you can see it. Every place it appears says so.
- **Real physics:** the animations are driven by a simple physics model. The induction motor follows a Kloss torque–slip curve. The synchronous motor's torque is proportional to sin δ, plus damper torque. So the rotor speeds up, pulls in and settles at a load angle realistically rather than being keyframed.
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
| Templestowe synchronous condenser | Mriya | CC BY-SA 3.0 |

- **Statistic:** the ≈ 45 % figure for electricity used by motor systems comes from IEA (2011), *Energy-Efficiency Policy Opportunities for Electric Motor-Driven Systems*, which estimates 43–46 %.
