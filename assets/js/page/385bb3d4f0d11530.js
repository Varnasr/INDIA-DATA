// The counts per polling part are in data/hyderabad/explorer.json, which
// scripts/build_hyderabad.py also reads.
SIR.json('data/hyderabad/explorer.json').then(function (D) {
const ACS=Object.keys(D.acs); let ac=ACS[0];
let P, T, E23; let sel=0, sortK='part', sortA=true; const charts={};
function loadAC(a){ac=a; const A=D.acs[a]; P=A.parts; T=A.total; E23=A.e2023; sel=0; sortK='part'; sortA=true;
  P.forEach(p=>{p.rate=pct(p.asd,p.total);p.hearrate=pct(p.hear,p.total);p.untr=pct(p.reasons[1],p.asd);p.frate=pct(p.f_asd,p.f_all);p.old=pct(p.age_asd[7],p.age_all[7]);});
  document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.ac===a));
  document.getElementById('tblTitle').textContent=A.partlabel==='part'?L('All {n} parts',{n:P.length}):L('All {n} polling-station names',{n:P.length});
  buildSide(); buildTable(); render(); window.scrollTo({top:0});}
const pct=(a,b)=>b?a/b*100:0, f=n=>n.toLocaleString('en-IN'), p1=x=>x.toFixed(1)+'%';
const col=r=>r<30?'#c9d6e3':r<45?'#7fa1c0':r<60?'#c0504d':'#7a1f1c';
const get=id=>P.find(p=>p.part===id)||T;
function chart(id,cfg){if(charts[id]){charts[id].destroy()}Chart.defaults.color=SIR.isDark()?'#D5DBE1':'#34495E';Chart.defaults.borderColor=SIR.isDark()?'rgba(255,255,255,0.1)':'rgba(0,0,0,0.08)';charts[id]=new Chart(document.getElementById(id),cfg)}
const base={responsive:true,plugins:{legend:{display:false}},scales:{x:{grid:{display:false}},y:{grid:{color:'#eef1f4'}}}};
function render(){
  const o=get(sel), whole=sel===0;
  document.getElementById('crumb').innerHTML=whole?L('Whole constituency'):'<button type="button">'+L('Whole constituency')+'</button> &rsaquo; '+L('Part {part}',{part:o.part});
  var back=document.querySelector('#crumb button'); if(back) back.addEventListener('click',function(){go(0);});
  document.getElementById('title').textContent=whole?(D.acs[ac].partlabel==='part'?L('{ac}, all {n} parts',{ac:ac,n:P.length}):L('{ac}, all {n} polling-station names',{ac:ac,n:P.length})):(ac==='Malakpet'?o.loc:(o.loc?L('Part {part}: {loc}',{part:o.part,loc:o.loc}):L('Part {part}',{part:o.part})));
  const hr=o.hear, clean=o.total-o.asd-hr-o.unacc;
  const avg=pct(T.asd,T.total); document.getElementById('sub').textContent=whole?L('{total} electors on the pre-revision roll. {deleted} left off the draft, {hearing} kept but called to a hearing, {untouched} untouched.',{total:f(o.total),deleted:p1(pct(o.asd,o.total)),hearing:p1(pct(hr,o.total)),untouched:p1(pct(clean,o.total))}):L('{total} electors. {rate} left off the draft against a constituency average of {avg}. {hearing} more were summoned to a hearing.',{total:f(o.total),rate:p1(o.rate),avg:p1(avg),hearing:f(hr)});
  const seg=[[o.asd,'var(--fill-red)','#fff'],[hr,'var(--fill-amber)','#1c2833'],[clean,'var(--fill-navy)','#fff'],[o.unacc,'#bbbbbb','#1c2833']];
  document.getElementById('fate').innerHTML=seg.map(([n,c,ink])=>`<div style="flex:${n};background:${c};color:${ink}">${pct(n,o.total)>9?f(n)+' ('+p1(pct(n,o.total))+')':''}</div>`).join('');
  const k=[[f(o.asd),L('names left off the draft')],[p1(pct(o.reasons[0]+o.reasons[1],o.asd)),L('of exclusions coded shifted or untraceable')],[p1(pct(o.age_asd[7],o.age_all[7])),L('of electors aged 80+ left off the draft ({n} on roll)',{n:f(o.age_all[7])})],[p1(pct(o.f_asd,o.asd)),L('of exclusions are women')],[T.haslink?p1(pct(o.asd-o.lk_asd,o.total-o.lk_all)):L('n/a'),T.haslink?L('left off among those with no 2002 link'):L('no 2002 linkage in this file')],[whole?f(T.median_slot):f(o.maxslot),whole?L('median hearing cases per part per slot'):L('most hearing cases in one slot')]];
  if(whole)k.push([(o.asd/E23.margin).toFixed(E23.margin<2000?0:1)+'\u00d7',L('the 2023 winning margin ({margin}, {name})',{margin:f(E23.margin),name:E23.name})],[p1(pct(o.asd,E23.valid)),L('of all valid votes cast in 2023')]);
  document.getElementById('kpis').innerHTML=k.map(([b,s])=>`<div><b>${b}</b><span>${s}</span></div>`).join('');
  chart('cReason',{type:'bar',data:{labels:D.reasons,datasets:[{data:o.reasons,backgroundColor:['#c0504d','#c0504d','#8c8c8c','#8c8c8c']}]},options:{...base,indexAxis:'y',plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>f(c.raw)+' ('+p1(pct(c.raw,o.asd))+')'}}},scales:{x:{grid:{color:'#eef1f4'}},y:{grid:{display:false}}}}});
  chart('cAge',{type:'bar',data:{labels:D.bands,datasets:[{data:o.age_asd.map((a,i)=>pct(a,o.age_all[i])),backgroundColor:'#1f4e79'}]},options:{...base,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>L('{pct} of {n}',{pct:p1(c.raw),n:f(o.age_all[c.dataIndex])})}}},scales:{x:{grid:{display:false}},y:{grid:{color:'#eef1f4'},max:100,ticks:{callback:v=>v+'%'}}}}});
  let gl=[L('Women'),L('Men'),L('Muslim-name'),L('Hindu-name')], gv=[pct(o.f_asd,o.f_all),pct(o.m_asd,o.m_all),pct(o.mus_asd,o.mus_all),pct(o.hin_asd,o.hin_all)], gn=[o.f_all,o.m_all,o.mus_all,o.hin_all];
  if(T.haslink){gl=gl.concat([L('Linked to 2002'),L('No 2002 link')]);gv=gv.concat([pct(o.lk_asd,o.lk_all),pct(o.asd-o.lk_asd,o.total-o.lk_all)]);gn=gn.concat([o.lk_all,o.total-o.lk_all]);}
  chart('cGroup',{type:'bar',data:{labels:gl,datasets:[{data:gv,backgroundColor:['#c0504d','#1f4e79','#c0504d','#1f4e79','#1f4e79','#c0504d']}]},options:{...base,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>L('{pct} of {n}',{pct:p1(c.raw),n:f(gn[c.dataIndex])})}}},scales:{x:{grid:{display:false}},y:{grid:{color:'#eef1f4'},max:100,ticks:{callback:v=>v+'%'}}}}});
  const hs=whole?D.acs[ac].daily:o.slots.map(([d,s,n])=>[d.slice(5)+' '+s,n]);
  document.getElementById('hearP').textContent=whole?L('Hearings scheduled per day across the constituency.'):L('Cases scheduled for this part, per date and slot.');
  chart('cHear',{type:'bar',data:{labels:hs.map(x=>x[0]),datasets:[{data:hs.map(x=>x[1]),backgroundColor:'#d9a400'}]},options:{...base,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>L('{n} cases',{n:f(c.raw)})}}},scales:{x:{grid:{display:false},ticks:{font:{size:9}}},y:{grid:{color:'#eef1f4'}}}}});
  chart('cRules',{type:'bar',data:{labels:D.rules,datasets:[{data:o.rules,backgroundColor:'#1f4e79'}]},options:{...base,indexAxis:'y',plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>L('{n} ({pct} of hearings)',{n:f(c.raw),pct:p1(pct(c.raw,o.hear))})}}},scales:{x:{grid:{color:'#eef1f4'}},y:{grid:{display:false},ticks:{font:{size:10}}}}}});
  document.querySelectorAll('#strip button,#partlist button').forEach(b=>b.classList.toggle('sel',+b.dataset.p===sel));
  if(!whole)document.getElementById('tablePanel').scrollIntoView({block:'nearest'});
}
function go(id){sel=id;render();window.scrollTo({top:0});}
function buildTabs(){document.getElementById('tabs').innerHTML=ACS.map(a=>`<button data-ac="${a}">${a}</button>`).join('');document.querySelectorAll('#tabs button').forEach(b=>b.onclick=()=>loadAC(b.dataset.ac));}
function buildSide(){
  const s=document.getElementById('strip'); s.style.gridTemplateColumns=`repeat(${P.length>250?22:18},1fr)`; s.innerHTML=P.map(p=>`<button data-p="${p.part}" title="${ac==='Malakpet'?L('{loc}: {rate} left off',{loc:p.loc,rate:p1(p.rate)}):L('Part {part} {loc}: {rate} left off',{part:p.part,loc:p.loc,rate:p1(p.rate)})}" style="background:${col(p.rate)}" aria-label="${L('Part {part}, {rate} left off',{part:p.part,rate:p1(p.rate)})}"></button>`).join('');
  s.querySelectorAll('button').forEach(b=>b.onclick=()=>go(+b.dataset.p));
  filter('');
}
function filter(q){q=q.toLowerCase();const ul=document.getElementById('partlist');ul.innerHTML=[T,...P].filter(p=>p.part===0||!q||String(p.part)===q||(p.loc||'').toLowerCase().includes(q)).map(p=>`<li><button data-p="${p.part}">${p.part?(ac==='Malakpet'?p.loc:(p.loc?L('Part {part} · {loc}',{part:p.part,loc:p.loc}):L('Part {part}',{part:p.part}))):L('Whole constituency')}<span class="rate">${p1(p.part?p.rate:pct(T.asd,T.total))}</span></button></li>`).join('');ul.querySelectorAll('button').forEach(b=>b.onclick=()=>go(+b.dataset.p));}
document.getElementById('q').addEventListener('input',e=>filter(e.target.value));
function buildTable(){const rows=[...P].sort((a,b)=>{const x=a[sortK],y=b[sortK];const c=typeof x==='string'?x.localeCompare(y):x-y;return sortA?c:-c});
  document.querySelector('#tbl tbody').innerHTML=rows.map(p=>`<tr data-p="${p.part}"><td>${p.part}</td><td>${p.loc||''}</td><td>${f(p.total)}</td><td>${f(p.asd)}</td><td>${p1(p.rate)}</td><td>${p1(p.hearrate)}</td><td>${p1(p.untr)}</td><td>${p1(p.frate)}</td><td>${p.age_all[7]?p1(p.old):''}</td><td>${p.maxslot}</td></tr>`).join('');
  document.querySelectorAll('#tbl tbody tr').forEach(r=>r.onclick=()=>go(+r.dataset.p));
  document.querySelectorAll('#tbl th').forEach(h=>h.classList.toggle('on',h.dataset.k===sortK));}
document.querySelectorAll('#tbl th').forEach(h=>h.onclick=()=>{if(sortK===h.dataset.k)sortA=!sortA;else{sortK=h.dataset.k;sortA=h.dataset.k==='part'||h.dataset.k==='loc'}buildTable()});
buildTabs();
// A link of the form #Yakutpura-297 opens that constituency at that part.
(function(){const m=SIR.hashId().match(/^([A-Za-z]+)(?:-(\d+))?$/);
  if(m&&ACS.includes(m[1])){loadAC(m[1]);if(m[2]&&P.some(p=>p.part===+m[2]))go(+m[2]);}else loadAC(ACS[0]);})();
document.addEventListener('sir-theme',()=>render());
}).catch(SIR.fail);
