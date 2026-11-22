"""Package clean-up for maximum compatibility (desktop PowerPoint, PowerPoint for iPhone/iPad/Android, web).

usage: python3 fix_package.py in.pptx out.pptx

1. docProps/app.xml is regenerated from the real content. The template's copy described the old 24-slide
   template (0 notes, 0 media clips, stale slide-title list).
2. The SharePoint document-library binding inherited from the corporate intranet template is removed:
   customXml/* (content-type schema, document-management properties, form templates) and the
   ContentTypeId custom property. The design, layouts, theme and PDO branding are untouched.
3. The package is rewritten cleanly: [Content_Types].xml first, every part deflated, no leftover
   relationships or content-type overrides pointing at removed parts.
"""
import re, sys, zipfile, posixpath
from lxml import etree

src, dst = sys.argv[1:3]
zin = zipfile.ZipFile(src)
names = zin.namelist()
drop = {n for n in names if n.startswith('customXml/')} | {'docProps/custom.xml'}
RNS = 'http://schemas.openxmlformats.org/package/2006/relationships'

def clean_rels(xml, rels_name):
    root = etree.fromstring(xml)
    base = posixpath.dirname(posixpath.dirname(rels_name))
    for r in list(root):
        if r.get('TargetMode') == 'External': continue
        t = r.get('Target'); t = t[1:] if t.startswith('/') else posixpath.normpath(posixpath.join(base, t))
        if t in drop: root.remove(r)
    return etree.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)

slides = [n for n in names if re.match(r'ppt/slides/slide\d+\.xml$', n)]
notes = [n for n in names if re.match(r'ppt/notesSlides/notesSlide\d+\.xml$', n)]
pres = zin.read('ppt/presentation.xml').decode()
hidden = sum(1 for n in slides if re.search(r'<p:sld [^>]*show="0"', zin.read(n).decode()[:1000]))
clips = sum(1 for n in slides if '<a:videoFile' in zin.read(n).decode())
words = sum(len(re.findall(r'<a:t>([^<]*)</a:t>', zin.read(n).decode())) for n in slides)
app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
       '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
       'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
       f'<TotalTime>0</TotalTime><Words>{words}</Words><Application>Microsoft Office PowerPoint</Application>'
       f'<PresentationFormat>Widescreen</PresentationFormat><Paragraphs>0</Paragraphs><Slides>{len(slides)}</Slides>'
       f'<Notes>{len(notes)}</Notes><HiddenSlides>{hidden}</HiddenSlides><MMClips>{clips}</MMClips>'
       '<ScaleCrop>false</ScaleCrop><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc>'
       '<HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion></Properties>')

ct = etree.fromstring(zin.read('[Content_Types].xml'))
for e in list(ct):
    if e.tag.endswith('Override') and e.get('PartName')[1:] in drop: ct.remove(e)
ct_xml = etree.tostring(ct, xml_declaration=True, encoding='UTF-8', standalone=True)

with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zout:
    zout.writestr('[Content_Types].xml', ct_xml)
    for n in names:
        if n == '[Content_Types].xml' or n in drop: continue
        if n == 'docProps/app.xml': data = app.encode()
        elif n.endswith('.rels'): data = clean_rels(zin.read(n), n)
        else: data = zin.read(n)
        zout.writestr(n, data)
print('removed', len(drop), 'parts; app.xml: slides', len(slides), 'notes', len(notes), 'hidden', hidden, 'clips', clips)
