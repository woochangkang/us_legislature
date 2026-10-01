const $=id=>document.getElementById(id);
const params=new URLSearchParams(location.search);
let data,marks,sources,source,page,evidence,documentTask,pdf,renderTask,generation=0,pdfLib;
const option=(value,label)=>{const o=document.createElement('option');o.value=value;o.textContent=label;return o;};
const errorMessage=()=>{$('status').textContent='PDF 렌더링을 사용할 수 없습니다. 인용 페이지 이미지가 있으면 대신 표시합니다. 원본 PDF는 위에서 다운로드할 수 있습니다.';};
async function getLibrary(){if(!pdfLib){pdfLib=await import('./vendor/pdfjs/build/pdf.mjs');pdfLib.GlobalWorkerOptions.workerSrc=new URL('./vendor/pdfjs/build/pdf.worker.mjs',import.meta.url).href;}return pdfLib;}
function updateLinks(){
 const url=new URL(location.href);url.search=new URLSearchParams({source:source.id,page:String(page),...(evidence?{evidence}: {})});history.replaceState(null,'',url);
 $('download').href=`pdfs/${source.file}#page=${page}`;$('official').href=source.url;
 $('page').value=page;$('page').max=source.pages;$('total').textContent=`/ ${source.pages}`;
 $('previous').disabled=page<=1;$('next').disabled=page>=source.pages;
 $('cited-pages').replaceChildren();
 Object.values(marks).filter(r=>r.source===source.id).sort((a,b)=>a.page-b.page).forEach(r=>{const a=document.createElement('a');a.href=`viewer.html?source=${source.id}&page=${r.page}${evidence?'&evidence='+evidence:''}`;a.textContent=r.page;if(r.page===page)a.setAttribute('aria-current','page');a.addEventListener('click',event=>{event.preventDefault();page=r.page;showPage();});$('cited-pages').append(a);});
 const ev=data.evidence.find(e=>e.id===evidence);$('claim').textContent=ev?ev.claim:source.title;$('explanation').textContent=ev?ev.assessment:'인용 페이지를 선택하면 관련 구절이 노란색으로 표시됩니다.';$('quote').textContent=ev?.quote||'';$('limit').textContent=ev?`해석의 한계: ${ev.limit}`:'';$('evidence-link').href=`index.html#${evidence||'sources'}`;
}
function focusPassage(){const first=$('highlights').firstElementChild;if(first)$('scroll-area').scrollTop=Math.max(0,first.offsetTop-100);else $('scroll-area').scrollTop=0;}
function drawHighlights(){
 const record=marks[`${source.id}:${page}`];const selected=(record?.highlights||[]).filter(h=>!evidence||h.evidence===evidence);
 $('highlights').replaceChildren();$('passages').replaceChildren();const seen=new Set();
 for(const h of selected){for(const r of h.rects){const key=r.join(',');if(seen.has(key))continue;seen.add(key);const box=document.createElement('span');box.className='highlight';Object.assign(box.style,{left:r[0]*100+'%',top:r[1]*100+'%',width:r[2]*100+'%',height:r[3]*100+'%'});$('highlights').append(box);}
 const p=document.createElement('p'),a=document.createElement('a');a.href=`index.html#${h.evidence}`;a.textContent=h.evidence;p.append(a,document.createTextNode(h.text));$('passages').append(p);}
 $('highlights').hidden=!$('highlight-toggle').checked;
 return selected.length;
}
async function showPage(){
 const token=++generation;if(renderTask){renderTask.cancel();renderTask=null;}
 updateLinks();const record=marks[`${source.id}:${page}`];const n=drawHighlights();
 $('canvas').hidden=true;$('facsimile').hidden=!record;
 if(record){$('facsimile').src=record.image;$('facsimile').onload=()=>{if(token===generation)focusPassage();};}
 $('paper').style.width=100*Number($('zoom').value)+'%';$('text').textContent=record?.text||'PDF에서 텍스트를 불러오는 중입니다.';
 $('status').textContent=`PDF ${page}쪽 · ${n?`${n}개 관련 구절 강조`:'선택된 근거의 강조 구절 없음'} · PDF를 불러오는 중…`;
 try{
 const currentPdf=await pdf;if(token!==generation)return;
 const pdfPage=await currentPdf.getPage(page);if(token!==generation)return;
 const width=$('paper').clientWidth||900;const viewport=pdfPage.getViewport({scale:width/pdfPage.getViewport({scale:1}).width});const ratio=Math.min(devicePixelRatio||1,2);
 const canvas=$('canvas');canvas.width=Math.floor(viewport.width*ratio);canvas.height=Math.floor(viewport.height*ratio);
 const task=pdfPage.render({canvasContext:canvas.getContext('2d'),viewport,transform:ratio===1?null:[ratio,0,0,ratio,0,0]});renderTask=task;await task.promise;if(token!==generation)return;renderTask=null;
 canvas.hidden=false;$('facsimile').hidden=true;focusPassage();$('status').textContent=`PDF ${page}쪽 · ${n?`${n}개 관련 구절 강조`:'선택된 근거의 강조 구절 없음'} · 원본 PDF 표시`;
 if(!record){const text=await pdfPage.getTextContent();if(token===generation)$('text').textContent=text.items.map(x=>x.str+(x.hasEOL?'\n':' ')).join('');}
 }catch(error){if(token!==generation||error.name==='RenderingCancelledException')return;errorMessage();}
}
async function loadSource(){
 source=sources.find(s=>s.id===$('source').value)||sources[0];page=Math.max(1,Math.min(Number(page)||1,source.pages));
 const choices=data.evidence.filter(e=>e.refs.some(r=>r.source===source.id));$('evidence').replaceChildren(option('','현재 페이지의 모든 근거'),...choices.map(e=>option(e.id,`${e.id} · ${e.claim}`)));
 if(!choices.some(e=>e.id===evidence))evidence='';$('evidence').value=evidence;
 if(documentTask){documentTask.destroy().catch(()=>{});documentTask=null;}
 pdf=getLibrary().then(lib=>{documentTask=lib.getDocument({url:`pdfs/${source.file}`,cMapUrl:'vendor/pdfjs/cmaps/',cMapPacked:true,standardFontDataUrl:'vendor/pdfjs/standard_fonts/',wasmUrl:'vendor/pdfjs/wasm/',iccUrl:'vendor/pdfjs/iccs/',disableAutoFetch:true,disableStream:true});return documentTask.promise;});
 await showPage();
}
try{
 [data,marks]=await Promise.all(['research-data.json','highlights.json'].map(async path=>{const r=await fetch(path);if(!r.ok)throw Error('자료를 읽을 수 없습니다');return r.json();}));
 sources=data.sources.filter(s=>s.file);$('source').replaceChildren(...sources.map(s=>option(s.id,s.title)));
 $('source').value=sources.some(s=>s.id===params.get('source'))?params.get('source'):'T';page=Number(params.get('page'))||111;evidence=params.get('evidence')||'';
 $('source').addEventListener('change',()=>{page=1;evidence='';loadSource();});
 $('evidence').addEventListener('change',()=>{evidence=$('evidence').value;const refs=data.evidence.find(e=>e.id===evidence)?.refs.filter(r=>r.source===source.id&&r.pdf_page);if(refs&&!refs.some(r=>r.pdf_page===page))page=refs[0].pdf_page;showPage();});
 $('page-form').addEventListener('submit',event=>{event.preventDefault();page=Math.max(1,Math.min(source.pages,Math.trunc(Number($('page').value))||1));showPage();});
 $('previous').addEventListener('click',()=>{if(page>1){page--;showPage();}});$('next').addEventListener('click',()=>{if(page<source.pages){page++;showPage();}});
 $('highlight-toggle').addEventListener('change',drawHighlights);$('zoom').addEventListener('change',showPage);
 let resize;window.addEventListener('resize',()=>{clearTimeout(resize);resize=setTimeout(showPage,180);});
 await loadSource();
}catch(error){$('claim').textContent='자료를 불러오지 못했습니다';errorMessage();}
