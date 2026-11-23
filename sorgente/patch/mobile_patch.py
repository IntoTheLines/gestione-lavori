# Adatta Lavori.html ai telefoni (Galaxy Z Flip 7, Fold 7 chiuso/aperto). Uso: python3 mobile_patch.py file...
import sys
CSS=r'''
/* ===== Telefono e Fold (fino a 900px) ===== */
#btnMore{display:none}
@media (max-width:900px){
  body{font-size:15px;-webkit-tap-highlight-color:transparent}
  header{padding:8px 12px calc(8px) 12px;gap:8px;padding-top:max(8px,env(safe-area-inset-top))}
  h1{font-size:17px;margin:0}
  #saveState{display:none}
  header .b{padding:8px 10px}
  #btnMore{display:inline-block}
  #btnFile,#btnExport,#btnImport{display:none}
  header.more #btnExport,header.more #btnImport{display:inline-block;flex:1}
  header.more #btnFile{display:inline-block;flex:1 1 100%}
  #userChip{padding:4px;min-width:44px;justify-content:center;font-size:0}#userChip .av{font-size:12px}
  #btnCloud{font-size:13px;padding:6px 10px;white-space:nowrap}
  header .spacer{flex:1 1 0}
  header{flex-wrap:nowrap}header.more{flex-wrap:wrap}
  h1{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0;flex:0 1 auto;font-size:16px}
  #btnCloud{max-width:46vw;overflow:hidden;text-overflow:ellipsis;flex:none}#userChip,#btnMore{flex:none}
  .tabs{position:fixed;left:0;right:0;bottom:0;z-index:20;display:flex;background:var(--card);border-top:1px solid var(--line);padding-bottom:env(safe-area-inset-bottom);box-shadow:0 -2px 12px rgba(0,0,0,.05)}
  .tabs button{flex:1;padding:8px 2px 9px;font-size:12px;border-bottom:0;border-top:3px solid transparent;display:flex;flex-direction:column;align-items:center;gap:2px}
  .tabs button::before{font-size:20px;line-height:1}
  .tabs button[data-tab=lavori]::before{content:"📋"}.tabs button[data-tab=team]::before{content:"👥"}
  .tabs button[data-tab=clienti]::before{content:"🏢"}.tabs button[data-tab=archivio]::before{content:"🗄️"}
  .tabs button.on{border-top-color:var(--acc);border-bottom:0;color:var(--acc)}
  main{padding:12px 12px calc(86px + env(safe-area-inset-bottom))}
  input,select,textarea,button.b{font-size:16px;min-height:42px}
  .bar{gap:8px}
  .bar #q,.bar #qc,.bar #qa{flex:1 1 100%;min-width:0!important;order:-1}
  .bar select{flex:1 1 calc(50% - 4px);min-width:0}
  .bar .hint{flex:1 1 100%}
  #viewSw{flex:1 1 100%}#viewSw button{flex:1;min-height:40px}
  #btnNewJob,#btnNewCli{position:fixed;right:16px;bottom:calc(78px + env(safe-area-inset-bottom));z-index:21;border-radius:28px;padding:14px 20px;box-shadow:0 6px 18px rgba(123,104,238,.45);font-weight:600}
  .sum{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
  .sum div{padding:8px 10px;min-width:0}.sum b{font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .sum span{font-size:11px}.netto{font-size:11px}
  /* lista come schede */
  .mgrp{margin-bottom:16px}
  .mgrid{display:grid;grid-template-columns:1fr;gap:8px}
  .mgrid .card{margin:0;padding:12px;border-left:4px solid var(--c,#ccc)}
  .grp.closed .mgrid{display:none}
  /* bacheca: colonne che scorrono di lato */
  .board{grid-template-columns:none;grid-auto-flow:column;grid-auto-columns:86vw;overflow-x:auto;scroll-snap-type:x mandatory;-webkit-overflow-scrolling:touch;padding-bottom:6px}
  .col{scroll-snap-align:start}
  /* clienti e archivio: solo le colonne utili */
  #clientsWrap th:nth-child(3),#clientsWrap td:nth-child(3),#clientsWrap th:nth-child(4),#clientsWrap td:nth-child(4),#clientsWrap th:nth-child(7),#clientsWrap td:nth-child(7){display:none}
  .ayr{margin:0 8px 8px 12px}
  .ayr th:nth-child(5),.ayr td:nth-child(5){display:none}
  .ayr th,.ayr td{padding:7px 6px;font-size:13px}
  .acli>summary{flex-wrap:wrap;padding:10px 12px}
  #archWrap .hint{font-size:12px}
  /* finestre a tutto schermo */
  dialog{width:100vw;max-width:100vw;height:100dvh;max-height:100dvh;margin:0;border-radius:0}
  dialog[open]{display:flex;flex-direction:column}
  dialog form{display:flex;flex-direction:column;height:100%}
  .db{flex:1;overflow:auto;grid-template-columns:1fr;align-content:start}
  .dh{padding-top:max(14px,env(safe-area-inset-top))}
  .df{flex-wrap:wrap;padding-bottom:max(12px,env(safe-area-inset-bottom))}
  .df .b{flex:1}
  #dCloud>div,#dFile>div{min-width:0!important;overflow:auto;flex:1}
  .lbox{padding:22px}
  #login{padding-bottom:calc(16px + env(safe-area-inset-bottom))}
}
/* Fold aperto (schermo largo quasi quadrato): due colonne, schede a lato */
@media (min-width:600px) and (max-width:900px){
  .mgrid{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
  .board{grid-auto-columns:calc(50% - 6px)}
  dialog{width:min(640px,72vw);height:100dvh;margin:0 0 0 auto;border-radius:16px 0 0 16px;box-shadow:-10px 0 40px rgba(0,0,0,.25)}
  .db{grid-template-columns:1fr 1fr}
  #clientsWrap th:nth-child(4),#clientsWrap td:nth-child(4){display:table-cell}
}
'''
JS=r'''
/* ---------- Telefono: schede al posto della tabella, menu ⋯, ridisegno quando il Fold si apre/chiude ---------- */
const isNarrow=()=>matchMedia("(max-width:900px)").matches;
$("#btnMore").onclick=e=>{e.stopPropagation();document.querySelector("header").classList.toggle("more")};
document.addEventListener("click",e=>{if(!e.target.closest("header"))document.querySelector("header").classList.remove("more")});
let _rsz,_wasNarrow=isNarrow();
window.addEventListener("resize",()=>{clearTimeout(_rsz);_rsz=setTimeout(()=>{const n=isNarrow();if(n!==_wasNarrow||n){_wasNarrow=n;render()}},200)});
'''
def patch(s):
    def rep(old,new):
        nonlocal s
        assert s.count(old)==1,old[:60]; s=s.replace(old,new)
    rep('</style>',CSS+'</style>')
    rep('<button class="b" id="userChip" title="Cambia utente"></button>','<button class="b" id="userChip" title="Cambia utente"></button>\n  <button class="b" id="btnMore" title="Altre funzioni">⋯</button>')
    # lista: su telefono schede raggruppate per stato
    rep('  const head=`<tr><th data-k="descrizione">',
'''  if(isNarrow()){
    $("#jobsWrap").innerHTML=groups.map(g=>`<div class="grp mgrp${collapsed[g.i]?" closed":""}">
      <div class="grph" data-st="${g.i}"><span class="caret">▾</span><span class="gtag" style="background:${COL[g.i]}">${g.s.toUpperCase()}</span><span class="cnt">${g.items.length}</span></div>
      <div class="mgrid">${g.items.map(j=>{const dc=dueCls(j);return `<div class="card" style="--c:${COL[g.i]}" data-id="${j.id}">
        <div class="ct">${esc(j.descrizione)}</div>${own(j)}<div class="hint">${esc(cliName(j.cliente))}</div>
        <div class="cm">${j.consegna?`<span class="${dc}">📅 ${fmtD(j.consegna)}${dc==="late"?" ⚠":""}</span>`:"<span></span>"}${j.importo?`<b>${eur(j.importo)}</b>`:""}</div>
        ${pagStato(j)>=0&&(scadOf(j)||j.dataPagamento)?`<div class="cm"><span class="hint">💶 ${pagStato(j)===2?"Pagato":"Scadenza"}</span><span>${payDateHtml(j)}</span></div>`:""}
        <div class="cm"><span><span class="prog"><i style="width:${+j.avanzamento||0}%"></i></span>${+j.avanzamento||0}%</span>${pagHtml(j)}</div>
        ${j.note?`<div class="note" style="margin-top:6px">${esc(j.note)}</div>`:""}</div>`}).join("")}</div></div>`).join("");
    $("#jobsWrap").querySelectorAll(".grph").forEach(h=>h.onclick=()=>{collapsed[h.dataset.st]=!collapsed[h.dataset.st];renderJobs()});
    $("#jobsWrap").querySelectorAll(".card").forEach(c=>c.onclick=()=>openJob(db.lavori.find(j=>j.id===c.dataset.id)));
    return;
  }
  const head=`<tr><th data-k="descrizione">''')
    rep('/* ---------- Clienti ---------- */',JS+'\n/* ---------- Clienti ---------- */')
    return s
if __name__=="__main__":
    for p in sys.argv[1:]:
        s=open(p,encoding='utf8').read();open(p,'w',encoding='utf8').write(patch(s));print("ok",p)
