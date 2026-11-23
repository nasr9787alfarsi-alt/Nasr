"""Construction-section configuration for v3 (objects come from the exported scene; see native_cfg.js)."""
CFG3 = {
  'induction': dict(
    overview=['frame', 'statorAsm', 'rotorAsm', 'bearingDE', 'bearingNDE', 'endShieldDE', 'endShieldNDE', 'fan', 'fanCover'],
    components=[
      dict(show=['statorAsm'], tag='statorCore'),
      dict(show=['rotorAsm'], tag='rotorCore'),
      dict(show=['cage'], replace={'rotorAsm': 'cage'}, tag='endRings'),
      dict(show=['shaft'], replace={'rotorAsm': 'shaft'}, tag='shaft'),
      dict(show=['bearingDE'], tag='bearingDE'),
      dict(show=['frame', 'endShieldDE', 'endShieldNDE'], join={'endShieldDE': 'frame', 'endShieldNDE': 'frame'}, tag='frame'),
      dict(show=['fan'], tag='fan'),
    ]),
  'sync': dict(
    overview=['cooling', 'frame', 'statorAsm', 'rotorAsm', 'shaftFan', 'sliprings', 'exciter', 'bearingDE', 'bearingNDE', 'endShieldDE', 'endShieldNDE'],
    components=[
      dict(show=['statorAsm'], tag='statorCore'),
      dict(show=['rotorAsm'], tag='rotorPoles'),
      dict(show=['fieldWinding'], replace={'rotorAsm': 'fieldWinding'}, tag='fieldWinding'),
      dict(show=['damper'], replace={'rotorAsm': 'damper'}, tag='damper'),
      dict(show=['sliprings'], tag='sliprings'),
      dict(show=['exciter'], tag='exciter'),
      dict(show=['frame', 'cooling', 'endShieldDE', 'endShieldNDE'], join={'cooling': 'frame', 'endShieldDE': 'frame', 'endShieldNDE': 'frame'}, tag='cooling'),
    ]),
}
