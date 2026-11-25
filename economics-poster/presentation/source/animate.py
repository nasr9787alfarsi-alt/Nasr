import json, re, sys, zipfile, shutil
src, dst = sys.argv[1], sys.argv[2]
anim = {int(k): v for k, v in json.load(open('anim.json')).items()}
FLOW_SLIDES = {k for k, v in anim.items() if len(v) == 8}
zin = zipfile.ZipFile(src); zout = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
report = []
for item in zin.infolist():
    data = zin.read(item.filename)
    m = re.match(r'ppt/slides/slide(\d+)\.xml$', item.filename)
    if m:
        n = int(m.group(1)); xml = data.decode('utf8')
        ids = dict((nm, i) for i, nm in re.findall(r'<p:cNvPr id="(\d+)" name="([^"]+)"', xml))
        ids = {v: k for k, v in ids.items()} if False else {nm: i for i, nm in re.findall(r'<p:cNvPr id="(\d+)" name="([^"]+)"', xml)}
        timing = ''
        steps = anim.get(n, [])
        if n in FLOW_SLIDES:
            steps = [steps[i] + steps[i + 4] for i in range(4)]
        if steps:
            ctn = [2]
            def nid():
                ctn[0] += 1; return ctn[0]
            clicks = []
            missing = 0
            for st in steps:
                spids = [ids[x] for x in st if x in ids]
                missing += len([x for x in st if x not in ids])
                effs = []
                for j, sp in enumerate(spids):
                    a, b, c = nid(), nid(), nid()
                    node = 'clickEffect' if j == 0 else 'withEffect'
                    effs.append(f'<p:par><p:cTn id="{a}" presetID="10" presetClass="entr" presetSubtype="0" fill="hold" nodeType="{node}"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                                f'<p:set><p:cBhvr><p:cTn id="{b}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn><p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl><p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
                                f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{c}" dur="500"/><p:tgtEl><p:spTgt spid="{sp}"/></p:tgtEl></p:cBhvr></p:animEffect></p:childTnLst></p:cTn></p:par>')
                o, i2 = nid(), nid()
                clicks.append(f'<p:par><p:cTn id="{o}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst><p:childTnLst><p:par><p:cTn id="{i2}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
                              + ''.join(effs) + '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>')
            timing = ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
                      '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>' + ''.join(clicks) +
                      '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
                      '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq></p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')
            report.append(f'slide {n}: {len(steps)} clicks, missing names {missing}')
        trans = '<p:transition spd="med"><p:fade/></p:transition>'
        assert '</p:clrMapOvr>' in xml and '<p:timing' not in xml
        xml = xml.replace('</p:clrMapOvr>', '</p:clrMapOvr>' + trans + timing, 1)
        data = xml.encode('utf8')
    zout.writestr(item, data)
zout.close()
print('\n'.join(report))
