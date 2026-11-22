"""Embedding / portability checks for the final deck."""
import zipfile, re, subprocess, sys, os, shutil, tempfile, json
deck = sys.argv[1]
z = zipfile.ZipFile(deck)
names = z.namelist()
media = [n for n in names if n.startswith('ppt/media/') and n.endswith(('.mp4', '.gif'))]
print('Embedded media parts:', len(media))
ext = []
for n in names:
    if n.endswith('.rels'):
        x = z.read(n).decode()
        for m in re.finditer(r'<Relationship [^>]*>', x):
            r = m.group(0)
            if 'TargetMode="External"' in r: ext.append((n, r))
print('External (linked) relationships:', len(ext)); [print('  ', e) for e in ext]
paths = [n for n in names if n.endswith('.xml') or n.endswith('.rels')]
bad = [n for n in paths if re.search(rb'(/tmp/|scratchpad|file://|C:\\\\)', z.read(n))]
print('Parts referencing local paths:', bad)
tmp = tempfile.mkdtemp()
for n in sorted(media):
    if not n.endswith('.mp4'): continue
    f = os.path.join(tmp, os.path.basename(n)); open(f, 'wb').write(z.read(n))
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,profile,level,width,height,pix_fmt,r_frame_rate:format=duration', '-of', 'json', f], capture_output=True, text=True).stdout)
    st = pr['streams'][0]; dec = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'null', '-'], capture_output=True, text=True)
    head = open(f, 'rb').read(64); faststart = head.find(b'moov') > 0 or open(f,'rb').read(200000).find(b'moov') < 100000
    print(f"  {os.path.basename(n):16s} {st['codec_name']} {st.get('profile')} L{st.get('level')} {st['width']}x{st['height']} {st['pix_fmt']} {st['r_frame_rate']} {float(pr['format']['duration']):.1f}s  decode_errors={len(dec.stderr.strip())>0}  moov_at_start={faststart}  size={os.path.getsize(f)/1e6:.1f}MB")
# slides with video and their timing nodes
for n in sorted([n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)], key=lambda s: int(re.findall(r'\d+', s)[0])):
    x = z.read(n).decode()
    if 'videoFile' in x:
        print(f"  {n}: videoFile={x.count('<a:videoFile')} p14:media={x.count('p14:media')} timing={'<p:timing' in x} transition={'<p:transition' in x}")
# isolated open test: copy deck alone into an empty folder and convert
iso = tempfile.mkdtemp(); shutil.copy(deck, iso)
print('Isolated copy folder contents:', os.listdir(iso))
shutil.rmtree(tmp)
