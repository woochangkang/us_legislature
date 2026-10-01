"""Add local PDF links and embedded highlighted viewers to the research HTML."""
from pathlib import Path
import json
from bs4 import BeautifulSoup

root=Path(__file__).resolve().parents[1];site=root/'ira'
data=json.loads((site/'research-data.json').read_text())
sources={s['id']:s for s in data['sources']}
soup=BeautifulSoup((site/'index.html').read_text(),'html.parser')
for e in data['evidence']:
 section=soup.find(id=e['id'])
 for r in e['refs']:
  if not r['pdf_page']:continue
  viewer=f"viewer.html?source={r['source']}&page={r['pdf_page']}&evidence={e['id']}"
  for a in section.select('a.reference'):
   if a.get('href')==r['url']:a['href']=viewer;a.string=f"PDF 하이라이트 · {r['locator']}";a.attrs.pop('target',None)
  r['viewer_url']=viewer
 refs=[r for r in e['refs'] if r['pdf_page']]
 if refs:
  detail=soup.new_tag('details',attrs={'class':'pdf-inline'})
  summary=soup.new_tag('summary');summary.string='이 자리에서 PDF와 하이라이트 보기';detail.append(summary)
  tabs=soup.new_tag('div',attrs={'class':'pdf-tabs'})
  for r in refs:
   a=soup.new_tag('a',href=r['viewer_url']);a.string=r['locator'];a['class']='pdf-tab';tabs.append(a)
  detail.append(tabs)
  iframe=soup.new_tag('iframe',attrs={'data-src':refs[0]['viewer_url'],'title':e['id']+' PDF 원문과 강조 표시','loading':'lazy'});detail.append(iframe)
  section.select_one('.evidence-body').append(detail)
 for block in section.select('blockquote'):
  mark=soup.new_tag('mark');mark.string=block.get_text();block.clear();block.append(mark)
for v in data['versions']:
 for r in v['refs']:
  r['official_url']=r.get('official_url',r['url'])
  r['url']=f"viewer.html?source={r['source']}&page={r['pdf_page']}"
for row in soup.select('#sources tbody tr'):
 sid=row.find('th').get_text(strip=True);source=sources.get(sid)
 if not source or not source.get('file'):continue
 td=row.find('td');a=td.find('a');a['href']=f'viewer.html?source={sid}&page=1';a.attrs.pop('target',None)
 p=soup.new_tag('small');link=soup.new_tag('a',href='pdfs/'+source['file'],download='');link.string='원본 PDF 다운로드';p.append(link);p.append(' · ');official=soup.new_tag('a',href=source['url'],target='_blank',rel='noopener');official.string='공식 출처';p.append(official);td.append(p)
css=soup.new_tag('link',rel='stylesheet',href='public.css');soup.head.append(css)
script=soup.new_tag('script',src='public.js');soup.body.append(script)
navlink=soup.new_tag('a',href='viewer.html?source=T&page=111&evidence=E02');navlink.string='PDF 원문 뷰어';soup.nav.append(navlink)
(site/'index.html').write_text(str(soup))
js=(site/'comparison.js').read_text();js='const versions='+json.dumps(data['versions'],ensure_ascii=False)+';\n'+js.split(';\n',1)[1];(site/'comparison.js').write_text(js)
(site/'research-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
print('Embedded highlighted PDF viewers in',sum(any(r['pdf_page'] for r in e['refs']) for e in data['evidence']),'evidence entries')
