set -e
B=/tmp/claude-0/-home-user-Nasr/9c8b2018-569a-5e1b-9ca8-bb1c1fb133d8/scratchpad/build
D=$B/../deliver2; R=/home/user/Nasr/motor-presentation
SK=/root/.claude/skills/synced/08b08bca-ae16-4991-94fe-78d4fad40ef2_bf56dd94-1b8e-4016-aaf9-bd4f64d1b9f6/pptx
cd $B
while pgrep -f "node video.js" >/dev/null; do sleep 30; done
for k in induction_motor_exploded synchronous_motor_exploded; do ffprobe -v error -show_entries format=duration -of csv=p=0 $D/video/$k.mp4; done
ffmpeg -v error -y -ss 9.6 -i $D/video/induction_motor_exploded.mp4 -frames:v 1 $D/img/poster_ind.png
ffmpeg -v error -y -ss 9.6 -i $D/video/synchronous_motor_exploded.mp4 -frames:v 1 $D/img/poster_syn.png
ffmpeg -v error -y -ss 33 -i $D/video/anim_induction.mp4 -frames:v 1 $D/img/poster_ind_anim.png; ffmpeg -v error -y -ss 37 -i $D/video/anim_sync.mp4 -frames:v 1 $D/img/poster_sync_anim.png
python3 build_brand.py
python3 $SK/scripts/office/validate.py $D/Inside_the_Motor_Induction_vs_Synchronous.pptx --original ../tpl/template.pptx | tail -3
ls -la $D/Inside_the_Motor_Induction_vs_Synchronous.pptx
