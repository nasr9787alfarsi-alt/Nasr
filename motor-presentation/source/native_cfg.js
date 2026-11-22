// Shared configuration for the PowerPoint-native 3D construction section (glb.js, partimg.js, build: native3d.py).
// "objects" are what appears on a slide: one PowerPoint 3D model (or picture in the backup deck) each.
// Parts that always travel together are one object, so separate objects never need to interpenetrate.
const D0 = [-0.62, 0.42, 1.0];           // overview view direction (from target towards camera)
const FOV_DEG = 15;                       // per-object camera field of view (mild perspective)
const CFG = {
  induction: {
    objects: {
      frame: ['frame'], statorAsm: ['statorCore', 'statorWinding'], rotorAsm: ['rotorCore', 'rotorBars', 'endRings', 'shaft'],
      cage: ['rotorBars', 'endRings'], shaft: ['shaft'], bearingDE: ['bearingDE'], bearingNDE: ['bearingNDE'],
      endShieldDE: ['endShieldDE'], endShieldNDE: ['endShieldNDE'], fan: ['fan'], fanCover: ['fanCover'],
    },
    overview: ['frame', 'statorAsm', 'rotorAsm', 'bearingDE', 'bearingNDE', 'endShieldDE', 'endShieldNDE', 'fan', 'fanCover'],
    components: [
      { show: ['statorAsm'], tag: 'statorCore' },
      { show: ['rotorAsm'], tag: 'rotorCore' },
      { show: ['cage'], replace: { rotorAsm: 'cage' }, tag: 'endRings' },
      { show: ['shaft'], replace: { rotorAsm: 'shaft' }, tag: 'shaft' },
      { show: ['bearingDE'], tag: 'bearingDE' },
      { show: ['frame', 'endShieldDE', 'endShieldNDE'], join: { endShieldDE: 'frame', endShieldNDE: 'frame' }, tag: 'frame' },
      { show: ['fan'], tag: 'fan' },
    ],
  },
  sync: {
    objects: {
      frame: ['frame'], cooling: ['cooling'], shaftFan: ['shaftFan'], statorAsm: ['statorCore', 'statorWinding'],
      rotorAsm: ['rotorPoles', 'fieldWinding', 'damper', 'shaft'], fieldWinding: ['fieldWinding'], damper: ['damper'], shaft: ['shaft'],
      sliprings: ['sliprings'], exciter: ['exciter'], bearingDE: ['bearingDE'], bearingNDE: ['bearingNDE'],
      endShieldDE: ['endShieldDE'], endShieldNDE: ['endShieldNDE'],
    },
    overview: ['cooling', 'frame', 'statorAsm', 'rotorAsm', 'shaftFan', 'sliprings', 'exciter', 'bearingDE', 'bearingNDE', 'endShieldDE', 'endShieldNDE'],
    components: [
      { show: ['statorAsm'], tag: 'statorCore' },
      { show: ['rotorAsm'], tag: 'rotorPoles' },
      { show: ['fieldWinding'], replace: { rotorAsm: 'fieldWinding' }, tag: 'fieldWinding' },
      { show: ['damper'], replace: { rotorAsm: 'damper' }, tag: 'damper' },
      { show: ['sliprings'], tag: 'sliprings' },
      { show: ['exciter'], tag: 'exciter' },
      { show: ['shaft'], replace: { rotorAsm: 'shaft' }, tag: 'shaft' },
      { show: ['bearingDE'], tag: 'bearingDE' },
      { show: ['frame', 'endShieldDE', 'endShieldNDE'], join: { endShieldDE: 'frame', endShieldNDE: 'frame' }, tag: 'frame' },
      { show: ['cooling', 'shaftFan'], join: { cooling: 'frame', shaftFan: 'frame' }, tag: 'cooling' },
    ],
  },
};
// camera basis for D0 (three.js lookAt convention): z' = D0, x' = up x z', y' = z' x x'
function basis(D) {
  const n = v => { const l = Math.hypot(...v); return v.map(a => a / l); };
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const z = n(D), x = n(cross([0, 1, 0], z)), y = cross(z, x); return { x, y, z };
}
module.exports = { CFG, D0, FOV_DEG, basis };
