document.querySelectorAll('.pdf-inline').forEach(detail=>{
 const frame=detail.querySelector('iframe');
 detail.addEventListener('toggle',()=>{if(detail.open&&!frame.getAttribute('src'))frame.src=frame.dataset.src;});
 detail.querySelectorAll('.pdf-tab').forEach(a=>a.addEventListener('click',event=>{if(event.ctrlKey||event.metaKey||event.shiftKey)return;event.preventDefault();frame.src=a.href;}));
});
