import sys, zipfile, re, collections
from lxml import etree
P="http://schemas.openxmlformats.org/presentationml/2006/main"; Aa="http://schemas.openxmlformats.org/drawingml/2006/main"
def words(path, skip_frames):
    z=zipfile.ZipFile(path); out={}
    n=len([f for f in z.namelist() if re.match(r'ppt/slides/slide\d+\.xml$',f)])
    for i in range(1,n+1):
        root=etree.fromstring(z.read(f'ppt/slides/slide{i}.xml')); ws=[]
        for sp in root.iter(f'{{{P}}}sp'):
            name=sp.find(f'.//{{{P}}}cNvPr').get('name')
            if skip_frames and 'counter frame' in name: continue
            for p in sp.iter(f'{{{Aa}}}p'):
                ws += ''.join(t.text or '' for t in p.iter(f'{{{Aa}}}t')).split()
        out[i]=collections.Counter(ws)
    return out
o=words(sys.argv[1],False); d=words(sys.argv[2],True)
print('slide count', len(o), len(d))
ok=True
for i in o:
    miss=o[i]-d[i]; extra=d[i]-o[i]
    if miss or extra: ok=False; print('slide',i,'MISSING',dict(miss),'EXTRA',dict(extra))
print('layout footer in new deck:', b'DEC MATCHA' in zipfile.ZipFile(sys.argv[2]).read('ppt/slideLayouts/slideLayout2.xml'))
print('ALL CONTENT MATCHES' if ok else 'DIFFERENCES FOUND')
