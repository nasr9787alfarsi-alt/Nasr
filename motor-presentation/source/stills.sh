O=../deliver/img
J='{"model":"induction","transparent":true,"w":2400,"h":1500}'
node still.js $O/ind_hero.png "STAGE.spin(0.4); STAGE.setCamera(new THREE.Vector3(-2.75,1.15,3.05), new THREE.Vector3(0.02,-0.03,0)); STAGE.render();" "$J"
node still.js $O/ind_cut.png "STAGE.cutaway(['frame','statorCore','statorWinding','endShieldDE','endShieldNDE','fanCover','bearingDE','bearingNDE'],true); STAGE.setCamera(new THREE.Vector3(-2.6,1.55,3.0), new THREE.Vector3(0,-0.03,0)); STAGE.render();" "$J"
node still.js $O/ind_statorrotor.png "STAGE.applyExplode(1); ['frame','endShieldDE','endShieldNDE','fan','fanCover','bearingDE','bearingNDE'].forEach(k=>STAGE.model.parts[k].group.visible=false); STAGE.setCamera(new THREE.Vector3(-1.9,1.35,3.9), new THREE.Vector3(-0.62,0.0,0)); STAGE.render();" "$J"
node still.js $O/ind_cage.png "['frame','endShieldDE','endShieldNDE','fan','fanCover','bearingDE','bearingNDE','statorCore','statorWinding'].forEach(k=>STAGE.model.parts[k].group.visible=false); STAGE.setPartAlpha(STAGE.model.parts.rotorCore,0.13,0); STAGE.setCamera(new THREE.Vector3(-1.5,0.75,1.65), new THREE.Vector3(-0.05,-0.02,0)); STAGE.render();" "$J"
S='{"model":"sync","transparent":true,"w":2400,"h":1500}'
node still.js $O/syn_hero.png "STAGE.setCamera(new THREE.Vector3(-3.35,1.55,3.85), new THREE.Vector3(0.12,0.1,0)); STAGE.render();" "$S"
node still.js $O/syn_cut.png "STAGE.cutaway(['frame','cooling','statorCore','statorWinding','endShieldDE','endShieldNDE','bearingDE','bearingNDE'],true); STAGE.setCamera(new THREE.Vector3(-3.3,1.85,3.8), new THREE.Vector3(0.1,0.1,0)); STAGE.render();" "$S"
R='{"transparent":true,"w":2000,"h":1250,"floorY":-0.62}'
node still.js $O/rot_salient.png "STAGE.setCamera(new THREE.Vector3(-1.9,1.0,2.4), new THREE.Vector3(0.05,0,0)); STAGE.render();" '{"model":"salient","transparent":true,"w":2000,"h":1250,"floorY":-0.45}'
node still.js $O/rot_cyl.png "STAGE.setCamera(new THREE.Vector3(-2.6,1.2,3.2), new THREE.Vector3(0,0,0)); STAGE.render();" '{"model":"cyl","transparent":true,"w":2000,"h":1250,"floorY":-0.45}'
node still.js $O/rot_brushless.png "STAGE.setCamera(new THREE.Vector3(-1.3,1.0,2.6), new THREE.Vector3(0.35,0,0)); STAGE.render();" '{"model":"brushless","transparent":true,"w":2000,"h":1250,"floorY":-0.45}'
