"""Locate verified evidence in immutable source PDFs. Requires PyMuPDF."""
from pathlib import Path
import json, re, hashlib
import fitz

ROOT = Path(__file__).resolve().parents[1] / 'ira'
data = json.loads((ROOT / 'research-data.json').read_text())
sources = {s['id']: s for s in data['sources'] if s.get('file')}
extra = {
 'M:3': ['Beginning five years after enactment', 'final assembly'],
 'T:110': ['I want to clarify the credit'],
 'T:111': ['as the person who wrote this, I want to clarify this', 'The second five years, no credit for anything that is not having final assembly in the United States'],
 'T:21': ['Schumer and I have been working on'],
 'T:105': ['after 2025'],
 'S:142': ['LIMITATION BASED ON PLACE OF ASSEMBLY'],
 'T:121': ['This requires that prior to the implementation of this bill', 'Chinese-produced electric vehicles'],
 'T:123': ['I am going to accept the Cornyn Amendment', 'I support the Amendment'],
 'T:124': ['I would like very much to be added as a co-sponsor of the Amendment'],
 'T:217': ['I will introduce the text of the Chairman’s mark as modified and amended', 'Senate Rule 14'],
 'T:218': ['will then write text from this conceptual markup'],
 'S:155': ['the final assembly of which is in the People’s Republic of China'],
 'H:1487': ['final assembly is within the United States'],
 'H:1494': ['the final assembly of such vehicle occurs', 'in the United States and operating under a collective'],
 'R:57': ['the final assembly of which occurs within North America'],
 'R:59': ['The amendments made by subsection (b) shall apply to vehicles sold after the date of enactment of this Act'],
 'I:386': ['shall apply to vehicles sold after the date of enactment of this Act', 'TRANSITION RULE'],
 'I:387': ['placed such vehicle in service on or after the date of enactment of this Act'],
 'E:144': ['shall apply to vehicles sold after the date of enactment of this Act'],
 'P:145': ['shall apply to vehicles sold after the date of enactment of this Act'],
 'P:146': ['entered into a written binding contract to purchase', 'placed such vehicle in service on or after the date of enactment of this Act'],
 'W:1': ['Mr. WARNOCK', 'Committee on Finance'],
}
def normal(text): return ''.join(c.lower() for c in text if c.isalnum())
def locate(page, phrase):
 words=page.get_text('words', sort=False)
 kept=[]
 for w in words:
  # Legislative line numbers interrupt quotations but are not part of their text.
  if w[4].isdigit() and int(w[4]) <= 30 and w[0] < 180: continue
  kept.append(w)
 chars=''; mapping=[]
 for i,w in enumerate(kept):
  part=normal(w[4]);chars+=part;mapping.extend([i]*len(part))
 target=normal(phrase);start=chars.find(target)
 if start<0: return []
 chosen=kept[mapping[start]:mapping[start+len(target)-1]+1]
 lines={}
 for w in chosen:
  key=(w[5],w[6]);r=fitz.Rect(w[:4])
  lines[key]=lines[key]|r if key in lines else r
 return [[round(r.x0/page.rect.width,6),round(r.y0/page.rect.height,6),round(r.width/page.rect.width,6),round(r.height/page.rect.height,6)] for r in lines.values()]

documents={k:fitz.open(ROOT/'pdfs'/s['file']) for k,s in sources.items()}
result={}; missed=[]
for ev in data['evidence']:
 for ref in ev['refs']:
  if not ref['pdf_page']: continue
  key=f"{ref['source']}:{ref['pdf_page']}";page=documents[ref['source']][ref['pdf_page']-1]
  record=result.setdefault(key,dict(source=ref['source'],page=ref['pdf_page'],width=page.rect.width,height=page.rect.height,highlights=[]))
  phrases=([ev['quote']] if ev['quote'] else [])+extra.get(key,[])
  matched=0
  for phrase in dict.fromkeys(phrases):
   rects=locate(page,phrase)
   if rects:
    record['highlights'].append(dict(evidence=ev['id'],text=phrase,rects=rects)); matched+=1
  if not matched: missed.append([ev['id'],key])

# Static facsimiles keep cited pages accessible even if PDF rendering is unavailable.
(ROOT/'pages').mkdir(exist_ok=True)
for key,record in result.items():
 page=documents[record['source']][record['page']-1]
 image=f"pages/{key.replace(':','-')}.webp"
 from PIL import Image
 pix=page.get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False)
 Image.frombytes('RGB',[pix.width,pix.height],pix.samples).save(ROOT/image,'WEBP',quality=85)
 record['image']=image
 record['text']=page.get_text()
for s in sources.values():
 actual=hashlib.sha256((ROOT/'pdfs'/s['file']).read_bytes()).hexdigest()
 assert actual==s['sha256'],s['file']
(ROOT/'highlights.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'pages':len(result),'passages':sum(len(x['highlights']) for x in result.values()),'unmatched_references':missed},ensure_ascii=False))
