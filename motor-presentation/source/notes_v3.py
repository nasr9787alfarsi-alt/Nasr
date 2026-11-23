# Timed speaker notes for v3 (exec'd by build_v3.py). Simple English for a non-electrical audience.
NOTES = {
'cover': ("0:25", """Good morning. In the next fifteen minutes we will look inside the two most important motors in industry – the induction motor and the synchronous motor. No electrical background is needed: we will see how they are built, how they work, and where each one is used."""),
'motor': ("0:40", """First, what does an electric motor actually do? [The slide animates by itself.]
Electricity goes in. Inside, copper coils turn it into magnetism – a magnetic field that turns. And that turning field pushes a shaft round: rotation comes out. That rotation drives pumps, fans, compressors and conveyors.
Motors are everywhere – they use about 45 percent of all the electricity in the world."""),
'families': ("0:40", """Two families of motor do most of that work. [The two dials turn by themselves.]
The induction motor is the workhorse: its rotor is pushed round by the magnetic field and always turns a little slower than the field – watch the left dial, the copper hand keeps falling behind.
The synchronous motor is the specialist: its rotor is a magnet of its own and turns exactly with the field – on the right the two hands stay together.
Keep this picture in mind – the rest of the talk explains it."""),
'sec1': ("0:06", """First: what is inside?"""),
'sr': ("0:30", """Every motor has two main parts. The stator is the fixed outer part: copper coils in a stack of thin steel sheets. It creates the magnetic field and never moves. The rotor is the turning part on the shaft. Between them is a tiny air gap – the magnetic field crosses it without touching anything."""),
'ih1': ("0:02", """[Automatic – the motor turns slowly into view.]"""),
'ih2': ("0:15", """Here is a complete induction motor – the kind you see on thousands of pumps and fans. On the next click we open it up: first the covers come off, then the inside slides apart."""),
'is1': ("0:02", """[Automatic – the covers lift away and the parts slide apart.]"""),
'io': ("0:20", """Seven main parts, numbered one to seven. We will now move in on each one. Keep an eye on the number, and on the small map in the corner that shows where the part sits."""),
'i1': ("0:15", """Number one, the stator – the fixed outer part. Copper coils sit in slots in a stack of thin steel sheets. They create the turning magnetic field."""),
'i2': ("0:14", """Number two, the rotor – the turning part inside the stator. The magnetic field pushes it round, and it turns the shaft."""),
'i3': ("0:18", """Number three is the heart of this motor: the rotor bars and end rings. We have removed the steel so you can see them. Bars joined by a ring at each end form a closed cage – the "squirrel cage". Nothing is wired to it: the turning field creates the current by itself. That is why this motor is so simple and reliable."""),
'i4': ("0:10", """Number four, the shaft – it carries the rotor and takes the turning force out to the machine."""),
'i5': ("0:12", """Number five, the bearings – one at each end. Steel balls roll between two rings so the shaft turns smoothly. They are the main wear part of the motor."""),
'i6': ("0:12", """Number six, the frame, with its end covers. It holds everything in line and protects it; the fins carry the heat away."""),
'i7': ("0:12", """And number seven, the cooling fan on the back of the shaft – it blows air along those fins. Seven parts: that is the whole induction motor."""),
'sh1': ("0:02", """[Automatic – the motor turns slowly into view.]"""),
'sh2': ("0:15", """Now a large synchronous motor – the kind used on big mills and compressors. Same idea: on the next click we open it up."""),
'ss1': ("0:02", """[Automatic – the housing and cooler lift away and the parts slide apart.]"""),
'so': ("0:20", """Seven main parts again. The stator is the same as before. What is new is in the rotor – and in how the rotor gets its own electricity."""),
's1': ("0:10", """Number one, the stator – built just like the induction motor's, and it makes the same turning field."""),
's2': ("0:15", """Number two, the rotor – and here the two motors differ. Its poles stick out like spokes. Each pole will become a fixed North or South magnet."""),
's3': ("0:15", """Number three, the field coils – copper coils wound round each pole. A DC current flows through them and turns the poles into magnets."""),
's4': ("0:15", """Number four, the damper bars – copper bars in the pole faces, a small cage like the induction motor's. They get the motor started."""),
's5': ("0:15", """Number five, the slip rings and brushes. The rotor spins, so how does the DC current get in? Carbon brushes press on rings on the shaft – a sliding contact."""),
's6': ("0:15", """Number six, the excitation system. This cabinet makes the DC current for the rotor coils, and sets how strong the rotor magnets are."""),
's7': ("0:15", """And number seven, the frame and cooling: a welded steel housing with a cooler on top. Inside, a fan on the shaft pushes warm air through the cooler. The shaft and the bearings do the same job as in the induction motor."""),
'sec2': ("0:06", """Now we switch them on – and make the invisible magnetism visible."""),
'rmf': ("0:50", """[Everything on this slide runs by itself – about 25 seconds.]
Both motors start with the same trick. Around the stator are three pairs of coils, each fed by one phase of the supply.
Watch the coils light up: the current in each coil rises and falls a moment after the one before – they take turns.
Together, they make ONE magnetic field, with a North and a South pole – and it turns round. Nothing moves mechanically; only the magnetism turns.
Put a magnet in the middle – like this compass needle – and the turning field drags it round.
The speed is fixed by the supply: 1500 rpm for a typical 4-pole motor on 50 hertz. Here it is slowed right down so we can follow it."""),
'ianim': ("1:00", """[Runs by itself – about 30 seconds.]
Here is the same turning field, with an induction rotor in the middle.
As the field sweeps over the rotor bars, it creates currents in them – shown in orange. No wires are connected: the field does it by itself.
Current and magnetic field push on each other – that turning force is called torque.
The rotor speeds up and chases the field… but never quite catches it. If it did, the field would stop sweeping over the bars, the current would vanish and so would the force.
So it always runs a little slower – about 2 percent. That lag is called slip. We have exaggerated it here so you can see it."""),
'sanim': ("1:00", """[Runs by itself – about 25 seconds.]
Same turning field again – now with a synchronous rotor, which has poles.
A rotor standing still cannot follow such a fast field, so it is started first: the damper bars spin it up like an induction motor.
Then DC current is switched on – the glow. The rotor becomes a magnet: its South pole is pulled towards the field's North pole.
Now it is locked in step: rotor and field turn together at exactly the same speed – 1500 rpm, zero slip.
When the load increases, the rotor just trails the field by a slightly bigger angle – but it never slows down."""),
'fund': ("0:50", """This is the heart of the comparison – three differences.
Rotor magnetism: in the induction motor, the turning field creates it – nothing is connected to the rotor. The synchronous motor needs its own DC supply to make fixed poles.
Slip: the induction rotor must lag a little, about 2 percent; the synchronous rotor does not lag at all.
Speed: on a 4-pole, 50-hertz motor the field turns at 1500 rpm. The induction motor runs at about 1470 and slows a little with load; the synchronous motor runs at exactly 1500, whatever the load."""),
'pros': ("0:45", """Neither motor is better – each is the right tool for different jobs.
The induction motor is simple, rugged, low-maintenance, starts by itself and costs less. Its speed drops slightly with load, it draws extra magnetising current from the grid, and changing its speed needs a drive.
The synchronous motor gives an exact speed, is very efficient in large sizes and can even help the plant's power supply. But it is more complex, needs a DC supply for its rotor and needs help to start.
In one line: induction by default; synchronous when the machine is very large or the speed must be exact."""),
'apps': ("0:40", """So where do we find them? Induction motors run everyday machines: pumps, fans, compressors, conveyors and air conditioning.
Synchronous motors drive the very large, constant-speed machines: grinding mills, cement plants, steel mills and large compressors and pumps. Some even run with no load at all, just to support the power grid."""),
'remember': ("0:30", """To wrap up. A motor turns electricity into rotation, using a turning magnetic field.
In the induction motor, the field drags the rotor round – always a little slower. Simple, and the default choice.
In the synchronous motor, the rotor is a DC magnet that locks onto the field – exact speed, for very large machines."""),
'thanks': ("0:05", """Thank you – questions?
Possible questions: Can an induction motor run exactly at field speed? Not as a motor. Why not use synchronous motors everywhere? Cost and complexity. What if a synchronous motor is overloaded? It falls out of step and its protection trips it."""),
}
assert len(KEYS) == len(prs.slides._sldIdLst)
elapsed = 0
for k, s in zip(KEYS, prs.slides):
    cue, body = NOTES[k]
    m, sec = cue.split(':'); elapsed += int(m) * 60 + int(sec)
    s.notes_slide.notes_text_frame.text = f"[Time: {cue}  ·  running total {elapsed // 60}:{elapsed % 60:02d}]\n\n" + body
print('scripted total', elapsed // 60, 'min', elapsed % 60, 's')
