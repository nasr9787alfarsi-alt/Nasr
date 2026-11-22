O=../deliver2/img
J='{"model":"induction","transparent":true,"light":true,"w":2400,"h":1500}'
S='{"model":"sync","transparent":true,"light":true,"w":2400,"h":1500}'
node still.js $O/ind_hero_l.png "STAGE.spin(0.4); STAGE.setCamera(new THREE.Vector3(-2.75,1.15,3.05), new THREE.Vector3(0.02,-0.03,0)); STAGE.render();" "$J"
node still.js $O/ind_cut_l.png "STAGE.cutaway(['frame','statorCore','statorWinding','endShieldDE','endShieldNDE','fanCover','bearingDE','bearingNDE'],true); STAGE.setCamera(new THREE.Vector3(-2.6,1.55,3.0), new THREE.Vector3(0,-0.03,0)); STAGE.render();" "$J"
node still.js $O/ind_statorrotor_l.png "STAGE.applyExplode(1); ['frame','endShieldDE','endShieldNDE','fan','fanCover','bearingDE','bearingNDE'].forEach(k=>STAGE.model.parts[k].group.visible=false); STAGE.setCamera(new THREE.Vector3(-2.2,1.5,4.7), new THREE.Vector3(-0.78,0.0,0)); STAGE.render();" "$J"
node still.js $O/ind_cage_l.png "['frame','endShieldDE','endShieldNDE','fan','fanCover','bearingDE','bearingNDE','statorCore','statorWinding'].forEach(k=>STAGE.model.parts[k].group.visible=false); STAGE.setPartAlpha(STAGE.model.parts.rotorCore,0.13,0); STAGE.setCamera(new THREE.Vector3(-1.5,0.75,1.65), new THREE.Vector3(-0.05,-0.02,0)); STAGE.render();" "$J"
node still.js $O/syn_hero_l.png "STAGE.setCamera(new THREE.Vector3(-3.35,1.55,3.85), new THREE.Vector3(0.12,0.1,0)); STAGE.render();" "$S"
node still.js $O/syn_cut_l.png "STAGE.cutaway(['frame','cooling','statorCore','statorWinding','endShieldDE','endShieldNDE','bearingDE','bearingNDE'],true); STAGE.setCamera(new THREE.Vector3(-3.3,1.85,3.8), new THREE.Vector3(0.1,0.1,0)); STAGE.render();" "$S"
node still.js $O/rot_salient_l.png "STAGE.setCamera(new THREE.Vector3(-2.4,1.2,3.0), new THREE.Vector3(0.1,0,0)); STAGE.render();" '{"model":"salient","transparent":true,"light":true,"w":2000,"h":1250,"floorY":-0.45}'
node still.js $O/rot_cyl_l.png "STAGE.setCamera(new THREE.Vector3(-3.3,1.5,4.0), new THREE.Vector3(-0.05,0,0)); STAGE.render();" '{"model":"cyl","transparent":true,"light":true,"w":2000,"h":1250,"floorY":-0.45}'
node still.js $O/rot_brushless_l.png "STAGE.setCamera(new THREE.Vector3(-1.9,1.25,3.2), new THREE.Vector3(0.3,0,0)); STAGE.render();" '{"model":"brushless","transparent":true,"light":true,"w":2000,"h":1250,"floorY":-0.45}'
