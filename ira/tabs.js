/* Progressive enhancement: original anchors remain usable without JavaScript. */
(() => {
  const groups=[];
  function makeGroup(container, items, label, side=false, existingNav=null) {
    if (!items.length) return;
    const nav=existingNav||document.createElement('div');
    nav.replaceChildren();nav.classList.add('tab-list');nav.setAttribute('role','tablist');
    nav.setAttribute('aria-label',label);nav.setAttribute('aria-orientation',side?'vertical':'horizontal');
    const group={container,items,nav,side};groups.push(group);
    for(const item of items){
      const button=document.createElement('button');button.type='button';button.id=`tab-${item.id}`;
      button.textContent=item.label;button.setAttribute('role','tab');button.setAttribute('aria-controls',item.panel.id);
      item.panel.setAttribute('role','tabpanel');item.panel.setAttribute('aria-labelledby',button.id);item.panel.tabIndex=0;
      item.button=button;button.addEventListener('click',()=>navigate(item.id));nav.append(button);
    }
    nav.addEventListener('keydown',event=>{
      const current=items.findIndex(x=>x.button===document.activeElement);if(current<0)return;
      const previous=side?'ArrowUp':'ArrowLeft',next=side?'ArrowDown':'ArrowRight';let index;
      if(event.key===previous)index=(current+items.length-1)%items.length;
      if(event.key===next)index=(current+1)%items.length;
      if(event.key==='Home')index=0;if(event.key==='End')index=items.length-1;
      if(index===undefined)return;event.preventDefault();navigate(items[index].id);items[index].button.focus({preventScroll:true});
    });
    if(side){
      container.classList.add('tab-workspace');
      container.prepend(nav);
      const labelNode=document.createElement('label');labelNode.className='mobile-tab-picker';labelNode.textContent=label;
      const picker=document.createElement('select');
      for(const item of items){const option=document.createElement('option');option.value=item.id;option.textContent=item.label;picker.append(option);}
      picker.addEventListener('change',()=>navigate(picker.value));labelNode.append(picker);container.prepend(labelNode);group.picker=picker;
    }else if(!existingNav){container.prepend(nav);}
    select(group,items[0]);return group;
  }
  function select(group,item){
    for(const x of group.items){const active=x===item;x.panel.hidden=!active;x.button.setAttribute('aria-selected',String(active));x.button.tabIndex=active?0:-1;}
    if(group.picker)group.picker.value=item.id;group.active=item;
    const detail=item.panel.matches('details.evidence')?item.panel:item.panel.querySelector('details.evidence');
    if(detail)detail.open=true;
  }
  function nested(section, selector, label, title){
    const elements=Array.from(section.querySelectorAll(selector));if(!elements.length)return;
    const workspace=document.createElement('div');section.insertBefore(workspace,elements[0].parentElement===section?elements[0]:elements[0].parentElement);
    const items=elements.map(element=>{
      const panel=document.createElement('div');panel.id=`panel-${element.id}`;panel.className='item-panel';workspace.append(panel);panel.append(element);
      return {id:element.id,label:title(element),panel};
    });makeGroup(workspace,items,label,true);
  }
  const main=document.querySelector('main');
  if(main?.id==='main'){
    const lead=main.querySelector('.lead-grid');if(lead)document.getElementById('finding').append(lead);
    const ids=['case-start','korean-stakes','procedure','actors','industry-impact','early-warning','research-library'];
    const labels=['1 사례의 질문','2 한국의 이해','3 입법 과정','4 주요 행위자','5 산업의 대응','6 조기경보','근거 자료실'];
    const nav=document.querySelector('header nav');
    const viewer=nav.querySelector('a[href^="viewer.html"]');if(viewer){viewer.classList.add('viewer-shortcut');document.querySelector('.mast').append(viewer);}
    makeGroup(main,ids.map((id,i)=>({id,label:labels[i],panel:document.getElementById(id)})),'연구 주제',false,nav);
    for(const id of ['stakes-workspace','library-workspace']){const area=document.getElementById(id);if(area)makeGroup(area,Array.from(area.querySelectorAll(':scope > section')).map(panel=>({id:panel.id,label:panel.dataset.caseLabel,panel})),id==='stakes-workspace'?'한국의 이해 탐색':'근거 자료 탐색');}
    const impact=document.getElementById('impact-workspace');
    if(impact)makeGroup(impact,Array.from(impact.querySelectorAll(':scope > section')).map(panel=>({id:panel.id,label:panel.dataset.impactLabel,panel})),'산업 영향 탐색');
    const procedure=document.getElementById('procedure-workspace');
    if(procedure)makeGroup(procedure,Array.from(procedure.querySelectorAll(':scope > section')).map(panel=>({id:panel.id,label:panel.dataset.procLabel,panel})),'의회 절차 탐색');
    nested(document.getElementById('actors'),'.actor-card','행위자 선택',e=>e.querySelector('h3').childNodes[0].textContent.trim());
    nested(document.getElementById('evidence'),'details.evidence','근거 선택',e=>`${e.id} · ${e.querySelector('.summary-main strong').textContent}`);
    nested(document.getElementById('questions'),'.question','조사 질문 선택',e=>`${e.id} · ${e.querySelector('h3').textContent}`);
    const order=document.querySelector('.plan-order');if(order){const details=document.createElement('details');details.className='plan-guide';const summary=document.createElement('summary');summary.textContent='조사 순서·계획 다운로드';details.append(summary);order.before(details);details.append(order);}
    document.body.classList.add('tabbed-site');
  }
  // Standalone report: headings become directly addressable report tabs.
  if(main?.classList.contains('report')){
    const cards=main.querySelector('.actor-grid');if(cards){
      const section=document.createElement('section');section.id='report-results';cards.before(section);section.append(cards);
      nested(section,'.actor-card','질문별 결과',e=>`${e.id.replace('result-','')} · ${e.querySelector('h3').textContent}`);
    }
    const resultsTitle=document.createElement('h2');resultsTitle.textContent='질문별 조사 결과';document.getElementById('report-results')?.before(resultsTitle);
    const headings=Array.from(main.querySelectorAll(':scope > h2'));
    const items=[];
    for(let i=0;i<headings.length;i++){
      const heading=headings[i],panel=document.createElement('section');panel.id=`report-section-${i}`;heading.before(panel);
      let node=heading;while(node&&node!==headings[i+1]){const next=node.nextSibling;panel.append(node);node=next;}
      items.push({id:panel.id,label:heading.textContent,panel});
    }
    // Outer group must activate before nested groups for deep links.
    const reportNav=document.createElement('nav');document.querySelector('header').append(reportNav);
    const group=makeGroup(main,items,'보고서 목차',false,reportNav);if(group){groups.splice(groups.indexOf(group),1);groups.unshift(group);}
    document.body.classList.add('tabbed-report');
  }
  function route(id,scroll=false){
    if(id==='main'&&main?.id==='main')id='case-start';
    const target=document.getElementById(id);
    if(!target)return;
    for(const group of groups){const item=group.items.find(x=>x.id===id||x.panel===target||x.panel.contains(target));if(item)select(group,item);}
    if(target.matches('details'))target.open=true;
    if(scroll){
      const outer=groups.find(g=>g.items.some(x=>x.id===id||x.panel.contains(target)));
      (outer?.active?.panel||target).scrollIntoView({block:'start',behavior:'instant'});
    }
  }
  function navigate(id){if(location.hash!==`#${id}`)history.pushState(null,'',`#${id}`);route(id,true);}
  function hashId(){try{return decodeURIComponent(location.hash.slice(1));}catch{return '';}}
  document.addEventListener('click',event=>{
    const a=event.target.closest('a[href^="#"]');if(!a||event.defaultPrevented||event.button!==0||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
    const id=a.getAttribute('href').slice(1);if(!document.getElementById(id))return;
    event.preventDefault();navigate(id);
  });
  window.addEventListener('hashchange',()=>route(hashId(),true));
  window.addEventListener('popstate',()=>route(hashId()||groups[0]?.items[0].id,true));
  const header=document.querySelector('header');
  if(header&&window.ResizeObserver)new ResizeObserver(()=>document.documentElement.style.setProperty('--tab-header-height',`${header.offsetHeight}px`)).observe(header);
  route(hashId());
})();
