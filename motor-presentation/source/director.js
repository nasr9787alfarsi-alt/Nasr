(function(){
const T=THREE, S=STAGE, ease=S.ease, easeIO=S.easeIO;
const V=(x,y,z)=>new T.Vector3(x,y,z);
const lerp=(a,b,t)=>a+(b-a)*t;
function camLerp(a,b,t){ return {pos:a.pos.clone().lerp(b.pos,t), tgt:a.tgt.clone().lerp(b.tgt,t)}; }

const TOURS = {
 induction: {
  title:'INDUCTION MOTOR', sub:'SQUIRREL-CAGE · TOTALLY ENCLOSED, FAN COOLED',
  camA:{pos:V(-2.9,1.3,3.4),tgt:V(0,-0.02,0)}, camA2:{pos:V(-2.2,1.5,3.9),tgt:V(0,0,0)},
  camE:{pos:V(-1.9,2.5,7.3),tgt:V(-0.2,0.25,0)},
  rotor:['rotorCore','rotorBars','endRings','shaft'], axis:[-2.5,2.25],
  tags:[['frame',11,[1420,110,'abs']],['statorCore',2,[1130,880,'abs']],['statorWinding',3,[740,330,'abs']],['rotorCore',5,[560,450,'abs']],['rotorBars',6,[540,850,'abs']],['endRings',7,[830,800,'abs']],['shaft',9,[330,520,'abs']],['bearingNDE',10,[1360,830,'abs']],['endShieldNDE',11,[1340,300,'abs']],['fan',12,[1660,400,'abs']]],
  steps:[
   {keys:['statorCore','statorWinding'], n:1, t:'Stator', d:'The stationary outer part. It never moves: a steel core with copper windings, fixed inside the frame.', chip:'STATIONARY', cam:{pos:V(-1.2,1.6,4.6),tgt:V(0.1,0.0,0)}},
   {keys:['statorCore'], n:2, t:'Stator Core', d:'Hundreds of thin, insulated steel sheets stacked together. They guide the magnetic field and keep losses low.', chip:'STATIONARY', cam:{pos:V(-1.0,1.5,4.2),tgt:V(0.1,0.0,0)}},
   {keys:['statorWinding'], n:3, t:'Stator Windings', d:'Insulated copper coils placed in the slots, in three groups (phases). AC current here creates the rotating magnetic field.', chip:'STATIONARY', phase:true, cam:{pos:V(0.6,1.4,4.2),tgt:V(0.2,0.0,0)}},
   {keys:['rotorCore','rotorBars','endRings','shaft'], n:4, t:'Rotor', d:'The rotating part inside the stator. It is pushed round by the magnetic field and turns the shaft.', chip:'ROTATING', spin:3.0, cam:{pos:V(-2.6,1.3,4.0),tgt:V(-1.3,0.0,0)}},
   {keys:['rotorCore'], n:5, t:'Rotor Core', d:'A laminated steel cylinder pressed onto the shaft. It carries the magnetic field through the rotor.', chip:'ROTATING', cam:{pos:V(-2.5,1.1,3.4),tgt:V(-1.3,0.0,0)}},
   {keys:['rotorBars','endRings'], n:6, t:'Rotor Bars', d:'Aluminium bars cast into slots around the rotor, slightly skewed. Current is induced in them – no wires are connected.', chip:'ROTATING', ghost:['rotorCore'], cam:{pos:V(-2.4,1.0,3.1),tgt:V(-1.3,0.0,0)}},
   {keys:['endRings'], n:7, t:'End Rings', d:'Short-circuit all the bars at both ends. Bars + rings form the closed “squirrel cage”.', chip:'ROTATING', ghost:['rotorCore'], also:['rotorBars'], cam:{pos:V(-2.0,1.0,3.0),tgt:V(-1.0,0.0,0)}},
   {keys:['airGap'], n:8, t:'Air Gap', d:'A very small gap (typically well under 2 mm) between stator and rotor. The magnetic field must cross it.', chip:'', assemble:true, also:['rotorCore','rotorBars','endRings','shaft','statorCore','statorWinding'], alsoA:1, cam:{pos:V(-2.3,0.75,0.95),tgt:V(-0.1,0.0,0)}},
   {keys:['shaft'], n:9, t:'Shaft', d:'Hardened steel shaft that carries the rotor and delivers the turning force (torque) to the pump, fan or machine.', chip:'ROTATING', cam:{pos:V(-2.9,1.0,3.3),tgt:V(-1.6,0.0,0)}},
   {keys:['bearingDE','bearingNDE'], n:10, t:'Bearings', d:'Ball bearings at each end support the shaft and let it spin smoothly with very little friction.', chip:'', cam:{pos:V(-1.0,1.2,3.4),tgt:V(-0.3,0.0,0)}},
   {keys:['frame','endShieldDE','endShieldNDE'], n:11, t:'Frame / Housing', d:'Cast-iron body and end shields. They hold the bearings, protect the inside and their fins release heat.', chip:'STATIONARY', cam:{pos:V(-2.4,2.6,6.6),tgt:V(-1.1,0.5,0)}},
   {keys:['fan','fanCover'], n:12, t:'Cooling Fan', d:'Fixed to the shaft. It blows outside air along the fins; the cover guards the fan and guides the air.', chip:'ROTATING', spin:4.0, cam:{pos:V(0.3,1.4,4.6),tgt:V(1.3,0.0,0)}},
  ]},
 sync: {
  title:'SYNCHRONOUS MOTOR', sub:'SALIENT-POLE ROTOR · SLIP RINGS & BRUSHES',
  camA:{pos:V(-3.5,1.7,4.1),tgt:V(0,0.12,0)}, camA2:{pos:V(-2.8,1.9,4.6),tgt:V(0.1,0.1,0)},
  camE:{pos:V(-1.9,3.3,9.8),tgt:V(-0.1,0.85,0)},
  rotor:['rotorPoles','fieldWinding','damper','shaft','shaftFan'], axis:[-2.95,2.5],
  tags:[['cooling',12,[1075,60,'abs']],['frame',11,[690,265,'abs']],['statorCore',2,[640,455,'abs']],['statorWinding',3,[1060,950,'abs']],['rotorPoles',5,[450,548,'abs']],['damper',6,[520,960,'abs']],['shaft',9,[300,835,'abs']],['sliprings',8,[1700,800,'abs']],['exciter',7,[1690,440,'abs']],['bearingNDE',10,[1440,880,'abs']]],
  steps:[
   {keys:['statorCore','statorWinding'], n:1, t:'Stator', d:'The stationary outer part – built just like an induction-motor stator: laminated core + three-phase winding.', chip:'STATIONARY', cam:{pos:V(-1.1,1.9,5.6),tgt:V(0.1,0.05,0)}},
   {keys:['statorCore'], n:2, t:'Stator Core', d:'Thin insulated steel sheets stacked together to guide the magnetic flux with low losses.', chip:'STATIONARY', cam:{pos:V(-0.9,1.7,5.0),tgt:V(0.1,0.05,0)}},
   {keys:['statorWinding'], n:3, t:'Three-Phase Stator Windings', d:'Three sets of copper coils (phases), each fed by one phase of the supply. Together they create the rotating magnetic field.', chip:'STATIONARY', phase:true, cam:{pos:V(0.7,1.6,5.0),tgt:V(0.2,0.05,0)}},
   {keys:['rotorPoles','fieldWinding','damper','shaft','shaftFan'], n:4, t:'Rotor (Salient-Pole)', d:'The rotating part. Its poles stick out (“salient”) and each becomes an electromagnet – the rotor has its OWN magnetic field.', chip:'ROTATING', spin:2.0, cam:{pos:V(-2.9,1.5,4.4),tgt:V(-1.5,0.05,0)}},
   {keys:['rotorPoles','fieldWinding'], n:5, t:'Rotor Poles & Field Winding', d:'Copper field coils wound around each steel pole. DC current through them makes fixed North and South poles.', chip:'ROTATING', cam:{pos:V(-2.7,1.3,3.6),tgt:V(-1.5,0.05,0)}},
   {keys:['damper'], n:6, t:'Damper (Starting) Bars', d:'Copper bars in the pole faces, shorted at the ends – a small squirrel cage used to start the motor and calm oscillations.', chip:'ROTATING', also:['rotorPoles'], alsoA:0.25, cam:{pos:V(-2.4,1.2,3.3),tgt:V(-1.4,0.05,0)}},
   {keys:['exciter','sliprings','fieldWinding'], n:7, t:'DC Excitation System', d:'An exciter supplies controlled DC to the field winding. Adjusting this current also adjusts the motor’s power factor.', chip:'', amber:true, cam:{pos:V(0.2,2.2,6.8),tgt:V(0.6,0.2,-0.3)}},
   {keys:['sliprings'], n:8, t:'Slip Rings & Brushes', d:'Bronze rings turn with the shaft; fixed carbon brushes slide on them, passing DC into the spinning rotor. (Brushless designs avoid this.)', chip:'', cam:{pos:V(1.4,1.1,3.2),tgt:V(2.2,0.05,0)}},
   {keys:['shaft'], n:9, t:'Shaft', d:'Forged steel shaft that carries the heavy rotor and transmits torque to the compressor, pump or mill.', chip:'ROTATING', cam:{pos:V(-3.4,1.2,4.0),tgt:V(-1.9,0.05,0)}},
   {keys:['bearingDE','bearingNDE'], n:10, t:'Bearings', d:'Support the rotor and keep it centred in the stator bore. Large machines often use oil-lubricated sleeve bearings.', chip:'', cam:{pos:V(-1.6,1.7,7.0),tgt:V(-0.6,0.05,0)}},
   {keys:['frame','endShieldDE','endShieldNDE'], n:11, t:'Frame / Housing', d:'Rigid welded steel frame and end shields: carries the stator and bearings, and bolts to the foundation.', chip:'STATIONARY', cam:{pos:V(-1.5,3.0,7.6),tgt:V(-0.2,0.7,0)}},
   {keys:['cooling','shaftFan'], n:12, t:'Cooling System', d:'Shaft fan circulates inside air through a top-mounted heat exchanger, where outside air carries the heat away.', chip:'', cam:{pos:V(-0.9,3.2,7.0),tgt:V(-0.4,1.2,0)}},
  ]}
};

window.DIRECTOR = { TOURS };
DIRECTOR.make = function(kind){
  const D = TOURS[kind]; const M = S.model;
  const tIntro=2.5, tExp=4.2, tOver=3.6, tStep=3.0, nS=D.steps.length, tOut=3.0;
  const t0Steps = tIntro+tExp+tOver, tEndSteps = t0Steps + nS*tStep, dur = tEndSteps + tOut;
  const allKeys = M.order;
  function alphaMap(step){
    const a={}; allKeys.forEach(k=>a[k]= M.parts[k].hiddenUntilFocus?0:0.10);
    if(!step) { allKeys.forEach(k=>a[k]= M.parts[k].hiddenUntilFocus?0:1); return a; }
    (step.also||[]).forEach(k=>a[k]=step.alsoA||0.9);
    (step.ghost||[]).forEach(k=>a[k]=0.08);
    step.keys.forEach(k=>a[k]=1);
    return a;
  }
  let spinAngle=0, lastT=0;
  function spinRate(t){
    if(t<t0Steps) return 0;
    if(t>=tEndSteps) return 0.6*(1-ease((t-tEndSteps)/1.2));
    const i=Math.min(nS-1,Math.floor((t-t0Steps)/tStep)); return D.steps[i].spin||0.6;
  }
  return { duration: dur, frame(t){
    // integrate spin
    const steps = Math.max(1, Math.ceil((t-lastT)/0.01)); if(t<lastT){spinAngle=0;lastT=0;}
    for(let i=0;i<steps && lastT<t;i++){ const dt=Math.min(0.01,t-lastT); spinAngle+=spinRate(lastT)*dt; lastT+=dt; }
    S.clearOverlay();
    const tagQ=[]; let cam, e=0, alphas=null, overrides={}, phaseK=0, glowKeys=[], glow=0, amber=false;
    if(t<tIntro){ cam=camLerp(D.camA,D.camA2,easeIO(t/tIntro)); e=0; S.title(D.title,D.sub,ease(t/0.6)); }
    else if(t<tIntro+tExp){ const u=(t-tIntro)/tExp; cam=camLerp(D.camA2,D.camE,easeIO(u)); e=u; S.title(D.title,D.sub,1-ease((t-tIntro)/0.8)); }
    else if(t<t0Steps){ const u=(t-tIntro-tExp); cam=D.camE; e=1; const a=ease(u/0.5)*(1-ease((u-tOver+0.45)/0.45));
      D.tags.forEach(([k,n,dir],i)=>{ const ai=Math.max(0,Math.min(1,(u-i*0.08)/0.35)); if(k&&M.parts[k]) tagQ.push([k,n,M.parts[k].label,ai*a,dir]); }); }
    else if(t<tEndSteps){
      const i=Math.floor((t-t0Steps)/tStep), u=(t-t0Steps)-i*tStep, st=D.steps[i], prev=i>0?D.steps[i-1]:null;
      const w=easeIO(u/0.7); e=1;
      cam=camLerp(prev?prev.cam:D.camE, st.cam, w);
      const a0=alphaMap(prev), a1=alphaMap(st); alphas={}; allKeys.forEach(k=>alphas[k]=lerp(a0[k],a1[k],w));
      if(!prev) allKeys.forEach(k=>alphas[k]=lerp(1,a1[k],w));
      // assemble for air gap
      if(st.assemble){ D.rotor.forEach(k=>overrides[k]=1-w); }
      if(prev&&prev.assemble){ D.rotor.forEach(k=>overrides[k]=w); }
      phaseK = (st.phase? w:0) + (prev&&prev.phase? (1-w):0);
      glowKeys=st.keys; glow=0.35*(0.5+0.5*Math.sin(u*4.2))*ease(u/0.6); amber=!!st.amber;
      const ca=ease((u-0.25)/0.45)*(1-ease((u-tStep+0.3)/0.3));
      S.caption(st.n, nS, st.t, st.d, st.chip, ca);
    } else {
      const u=(t-tEndSteps)/tOut; cam=camLerp(D.steps[nS-1].cam, D.camA, easeIO(u)); e=1-easeIO(u/0.85);
      const last=alphaMap(D.steps[nS-1]); alphas={}; allKeys.forEach(k=>alphas[k]=lerp(last[k], M.parts[k].hiddenUntilFocus?0:1, ease(u/0.3)));
      S.title(D.title,D.sub,ease((u-0.7)/0.3));
    }
    S.applyExplode(e, overrides);
    S.spin(spinAngle);
    allKeys.forEach(k=>{ const p=M.parts[k]; const a = alphas? alphas[k] : (p.hiddenUntilFocus?0:1); p.group.visible = a>0.01;
      const g = glowKeys.includes(k)? glow : 0; S.setPartAlpha(p, a, g);
      if(amber && glowKeys.includes(k)) p.materials().forEach(m=>{ if(m.emissive) m.emissive.setRGB((S.light?0.18:0.5)*g,(S.light?0.08:0.22)*g,0.01*g); });
    });
    if(M.parts.airGap){ M.parts.airGap.materials().forEach(m=>{ m.opacity = 0.85*(alphas?alphas.airGap:0); }); }
    S.setPhaseColors(M.parts.statorWinding, phaseK);
    S.setCamera(cam.pos, cam.tgt); S.camera.updateMatrixWorld();
    if(t>=tIntro && t<t0Steps) S.axisLine(D.axis[0], D.axis[1], 0.55*Math.min(1,e*1.5)*(t<tIntro+tExp+tOver-0.4?1:Math.max(0,(t0Steps-t)/0.4)));
    tagQ.forEach(a=>S.tag(...a));
    S.render();
  }};
};
})();
