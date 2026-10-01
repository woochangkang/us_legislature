# coding: utf-8
"""Generate a typographic share card; Pillow and a Korean font are required."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from bs4 import BeautifulSoup
import os
R=Path(__file__).resolve().parents[1];P=R/'ira';scale=2
font_path=os.environ.get('IRA_KOREAN_FONT','/System/Library/Fonts/AppleSDGothicNeo.ttc')
im=Image.new('RGB',(1200*scale,630*scale),'#152642');d=ImageDraw.Draw(im)
def font(size,bold=False):return ImageFont.truetype(font_path,size*scale,index=6 if bold else 4)
def text(x,y,value,size=30,color='#ffffff',bold=False):d.text((x*scale,y*scale),value,font=font(size,bold),fill=color)
def box(x,y,w,h,fill,outline=None):d.rounded_rectangle((x*scale,y*scale,(x+w)*scale,(y+h)*scale),radius=16*scale,fill=fill,outline=outline,width=2*scale)
d.rectangle((0,0,16*scale,630*scale),fill='#73cec2')
text(65,42,'IRA  |  입법 조기경보 사례 연구',26,'#86d7d0',True)
text(65,109,'법이 바뀌기 전에,',66,bold=True)
text(65,191,'산업은 무엇을 알아야 했나',66,bold=True)
text(68,293,'한국 자동차산업의 이해관계로 읽는 IRA 제정 과정',30,'#d5e0ed')
for x,w,label,sub in [(65,338,'북미 조립 · 시행 유예','한국 산업의 이해'),(447,293,'입법 과정 · 행위자','조건이 바뀌는 경로'),(784,350,'조기경보 · 대응','산업의 준비 시간')]:
 box(x,381,w,127,'#223c59','#3c617a');text(x+22,403,label,29,bold=True);text(x+22,448,sub,24,'#b6d4e2')
for x in [413,750]:
 d.line((x*scale,443*scale,(x+24)*scale,443*scale),fill='#86d7d0',width=3*scale)
 d.line(((x+15)*scale,435*scale,(x+24)*scale,443*scale,(x+15)*scale,451*scale),fill='#86d7d0',width=3*scale)
text(68,561,'공식 기록 · 조문 변화 · 산업 대응',22,'#a8bdd1')
text(879,559,'입법 증거 아틀라스',23,'#d4e3ed',True)
im.resize((1200,630),Image.Resampling.LANCZOS).save(P/'assets/ira-share-v1.png',optimize=True)
f=P/'index.html';s=BeautifulSoup(f.read_text(),'html.parser');base='https://woochangkang.github.io/us_legislature/ira/'
meta={'og:type':'website','og:locale':'ko_KR','og:site_name':'입법 증거 아틀라스','og:title':'IRA 사례 연구 | 한국 자동차산업과 입법 조기경보','og:description':'북미 조립과 시행 유예는 어떻게 바뀌었나? 한국 산업의 이해관계에서 IRA 입법 과정·주요 행위자·조기경보의 필요성까지 살펴봅니다.','og:url':base,'og:image':base+'assets/ira-share-v1.png','og:image:type':'image/png','og:image:width':'1200','og:image:height':'630','og:image:alt':'법이 바뀌기 전에, 산업은 무엇을 알아야 했나. 북미 조립·시행 유예에서 입법 과정과 조기경보로 이어지는 IRA 사례 연구.'}
for k,v in meta.items():
 old=s.find('meta',property=k)
 if old:old.decompose()
 s.head.append(s.new_tag('meta',attrs={'property':k,'content':v}))
for k,v in {'twitter:card':'summary_large_image','twitter:title':meta['og:title'],'twitter:description':meta['og:description'],'twitter:image':meta['og:image'],'twitter:image:alt':meta['og:image:alt']}.items():
 old=s.find('meta',attrs={'name':k})
 if old:old.decompose()
 s.head.append(s.new_tag('meta',attrs={'name':k,'content':v}))
old=s.find('link',rel='canonical')
if old:old.decompose()
s.head.append(s.new_tag('link',rel='canonical',href=base));f.write_text(str(s))
print('Generated share card and static Open Graph metadata')
