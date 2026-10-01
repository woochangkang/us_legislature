(()=>{
 const picker=document.getElementById('impact-chart-picker'),image=document.getElementById('impact-chart'),caption=document.getElementById('impact-chart-caption');
 if(!picker||!image)return;
 const base=image.getAttribute('src').replace(/monthly\.svg$/,'');
 picker.addEventListener('change',()=>{
 const monthly=picker.value==='monthly';image.src=base+(monthly?'monthly.svg':'annual.svg');
 image.alt=monthly?'2022년 6–12월 아이오닉 5 판매: 2853, 1978, 1516, 1306, 1579, 1191, 1720대':'2022–2025 아이오닉 5·6, EV6·EV9 연간 판매 비교. 아래 표에 정확한 값과 출처 제공.';
 caption.textContent=monthly?'8월은 제정 전후가 섞인 달이다. 점선은 제정 시점이며 인과효과 추정선이 아니다.':'2025년은 현지 생산과 차량 공제 종료가 겹친 별도 국면이다. 미출시 연도는 선을 연결하지 않았다.';
 });
})();
