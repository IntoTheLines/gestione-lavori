# Aggiunge: N. fattura nei lavori + sezione Appunti (sincronizzata). Uso: python3 feature_appunti_patch.py file...
import sys
CSS=r'''
/* ----- Appunti ----- */
.nlist{display:grid;gap:8px;grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}
.ncard{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--acc);border-radius:8px;padding:10px 12px;cursor:pointer;display:flex;gap:10px;align-items:flex-start}
.ncard:hover{box-shadow:0 3px 10px rgba(0,0,0,.08)}
.ncard.done{opacity:.55}.ncard.done .ntxt{text-decoration:line-through}
.ncard.nlate{border-left-color:var(--red)}.ncard.ntoday{border-left-color:var(--amber)}
.ncard .ck{width:22px;height:22px;min-height:0;flex:none;margin:1px 0 0;accent-color:var(--acc)}
.nbody{flex:1;min-width:0}
.ndate{font-size:12px;font-weight:600;color:var(--muted)}.nlate .ndate{color:var(--red)}.ntoday .ndate{color:var(--amber)}
.ntxt{white-space:pre-wrap;margin:3px 0 6px;word-break:break-word}
.nchips{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.chip{font-size:12px;background:#f0f2f5;border-radius:999px;padding:2px 9px;color:#374151}.chip.sh{background:#efedfd;color:var(--acc)}
.chip.lk{cursor:pointer}.chip.lk:hover{background:#e2e5ea}
.nh{font-weight:700;font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;margin:16px 2px 8px}
.nh:first-child{margin-top:4px}
.chk{display:flex!important;flex-direction:row!important;align-items:center;gap:8px;color:var(--ink)!important;font-size:14px!important}
.chk input{width:20px;height:20px;min-height:0}
@media (max-width:900px){.tabs button[data-tab=appunti]::before{content:"📝"}}
'''
SECTION=r'''  <section id="tab-appunti" hidden>
    <div class="bar">
      <button class="b p" id="btnNewNote">+ Nuovo appunto</button>
      <input id="qn" placeholder="Cerca negli appunti…" style="min-width:200px">
      <select id="fNote"><option value="tutti">Miei e condivisi</option><option value="miei">Solo i miei</option><option value="team">Condivisi dal team</option></select>
      <label class="hint chk"><input type="checkbox" id="fNoteDone"> Mostra fatti</label>
    </div>
    <div id="notesWrap"></div>
  </section>

  <section id="tab-clienti" hidden>'''
DIALOG=r'''<dialog id="dNote">
  <form method="dialog" id="formNote">
    <div class="dh" id="dNoteTitle">Appunto</div>
    <div class="db">
      <label>Data<input type="date" id="nData"></label>
      <label>Ora (facoltativa)<input type="time" id="nOra"></label>
      <label class="full">Appunto<textarea id="nTesto" required style="min-height:120px" placeholder="Scrivi qui…"></textarea></label>
      <label>Cliente (facoltativo)<select id="nCli"></select></label>
      <label>Lavoro (facoltativo)<select id="nJob"></select></label>
      <label class="full chk"><input type="checkbox" id="nShare"> 👥 Condividi con il team</label>
      <label class="full chk"><input type="checkbox" id="nDone"> ✔ Fatto</label>
    </div>
    <div class="df"><button type="button" class="b d" id="btnDelNote">Elimina</button><div class="spacer"></div>
      <button type="button" class="b" onclick="this.closest('dialog').close()">Annulla</button><button class="b p" id="btnSaveNote">Salva</button></div>
  </form>
</dialog>

<dialog id="dJob">'''
JS=r'''/* ---------- Appunti ---------- */
let editNote=null;
const noteVis=n=>n.utente===me||n.condiviso;
function fillNoteSelects(cli,job){
  const cs=[...db.clienti].sort((a,b)=>a.nome.localeCompare(b.nome));
  $("#nCli").innerHTML='<option value="">— nessuno —</option>'+cs.map(c=>`<option value="${c.id}">${esc(c.nome)}</option>`).join("");
  $("#nCli").value=cli||"";fillNoteJobs(job)}
function fillNoteJobs(job){
  const c=$("#nCli").value;
  const js=db.lavori.filter(j=>!c||j.cliente===c).sort((a,b)=>(b.consegna||"").localeCompare(a.consegna||""));
  $("#nJob").innerHTML='<option value="">— nessuno —</option>'+js.map(j=>`<option value="${j.id}">${esc(j.descrizione)}${c?"":" · "+esc(cliName(j.cliente))}</option>`).join("");
  $("#nJob").value=js.some(j=>j.id===job)?job:""}
$("#nCli").onchange=()=>fillNoteJobs($("#nJob").value);
$("#nJob").onchange=()=>{const j=db.lavori.find(x=>x.id===$("#nJob").value);if(j&&!$("#nCli").value){$("#nCli").value=j.cliente||"";fillNoteJobs(j.id)}};
function openNote(n,pre){
  editNote=n||null;const ro=!!n&&n.utente!==me;
  $("#dNote").classList.toggle("ro",ro);
  $("#formNote").querySelectorAll(".db input,.db select,.db textarea").forEach(el=>el.disabled=ro);
  $("#dNoteTitle").innerHTML=ro?`Appunto di ${esc(userName(n.utente))} <span class="hint">(solo consultazione)</span>`:n?"Modifica appunto":"Nuovo appunto";
  $("#nData").value=n?n.data||"":(pre?.data??today());$("#nOra").value=n?.ora||"";$("#nTesto").value=n?.testo||"";
  fillNoteSelects(n?.cliente??pre?.cliente,n?.lavoro??pre?.lavoro);
  $("#nShare").checked=n?!!n.condiviso:!!pre?.condiviso;$("#nDone").checked=!!n?.fatto;
  $("#btnDelNote").style.visibility=n&&!ro?"visible":"hidden";$("#btnSaveNote").style.display=ro?"none":"";
  $("#dNote").showModal();if(!n)setTimeout(()=>$("#nTesto").focus(),50)}
$("#formNote").onsubmit=e=>{
  e.preventDefault();if(editNote&&editNote.utente!==me)return;
  let n=editNote?db.appunti.find(x=>x.id===editNote.id):null;
  if(!n){n={id:uid(),creato:today(),utente:me};db.appunti.push(n)}
  Object.assign(n,{data:$("#nData").value,ora:$("#nOra").value,testo:$("#nTesto").value.trim(),cliente:$("#nCli").value,lavoro:$("#nJob").value,
    condiviso:$("#nShare").checked,fatto:$("#nDone").checked});
  touch(n);delete db.eliminati[n.id];save();$("#dNote").close();render()};
$("#btnDelNote").onclick=()=>{if(editNote&&confirm("Eliminare questo appunto?")){db.appunti=db.appunti.filter(x=>x.id!==editNote.id);markDel(editNote.id);save();$("#dNote").close();render()}};
$("#btnNewNote").onclick=()=>openNote();
$("#qn").oninput=()=>renderNotes();$("#fNote").onchange=()=>renderNotes();$("#fNoteDone").onchange=()=>renderNotes();
function renderNotes(){
  const q=$("#qn").value.toLowerCase(),f=$("#fNote").value,showDone=$("#fNoteDone").checked,t=today();
  const jobName=id=>(db.lavori.find(j=>j.id===id)||{}).descrizione;
  let list=db.appunti.filter(n=>noteVis(n)&&(f==="tutti"||(f==="miei"?n.utente===me:n.utente!==me))&&(showDone||!n.fatto)
    &&(!q||(n.testo+" "+cliName(n.cliente)+" "+(jobName(n.lavoro)||"")).toLowerCase().includes(q)));
  if(!list.length){$("#notesWrap").innerHTML=`<div class="empty">${db.appunti.some(noteVis)?"Nessun appunto da mostrare.":"Nessun appunto. Clicca <b>+ Nuovo appunto</b>: scegli tu la data, e se vuoi lo colleghi a un cliente o a un lavoro."}</div>`;return}
  const key=n=>(n.data||"9999")+(n.ora||"99");list.sort((a,b)=>key(a).localeCompare(key(b)));
  const grp=n=>n.fatto?"Fatti":!n.data?"Senza data":n.data<t?"In ritardo":n.data===t?"Oggi":"Prossimi";
  const order=["In ritardo","Oggi","Prossimi","Senza data","Fatti"];
  const card=n=>{const g=grp(n),cls=n.fatto?"done":g==="In ritardo"?"nlate":g==="Oggi"?"ntoday":"";const mine=n.utente===me;
    const jn=n.lavoro&&jobName(n.lavoro);
    return `<div class="ncard ${cls}" data-id="${n.id}">${mine?`<input type="checkbox" class="ck" data-id="${n.id}" ${n.fatto?"checked":""} title="Fatto">`:""}
      <div class="nbody"><div class="ndate">${n.data?"📅 "+fmtD(n.data)+(n.ora?" · "+n.ora:""):"Senza data"}</div>
      <div class="ntxt">${esc(n.testo)}</div>
      <div class="nchips">${n.cliente?`<span class="chip">🏢 ${esc(cliName(n.cliente))}</span>`:""}${jn?`<span class="chip lk" data-job="${n.lavoro}">📋 ${esc(jn)}</span>`:""}
      ${n.condiviso?'<span class="chip sh">👥 Condiviso</span>':""}${!mine?`<span class="owner">${avatar(n.utente,1)} ${esc(userName(n.utente))}</span>`:""}</div></div></div>`};
  $("#notesWrap").innerHTML=order.map(g=>{const it=list.filter(n=>grp(n)===g);return it.length?`<div class="nh">${g} · ${it.length}</div><div class="nlist">${it.map(card).join("")}</div>`:""}).join("");
  const w=$("#notesWrap");
  w.querySelectorAll(".ncard").forEach(c=>c.onclick=e=>{if(e.target.closest(".ck,.lk"))return;openNote(db.appunti.find(n=>n.id===c.dataset.id))});
  w.querySelectorAll(".ck").forEach(c=>c.onchange=()=>{const n=db.appunti.find(x=>x.id===c.dataset.id);if(n){n.fatto=c.checked;touch(n);save();renderNotes()}});
  w.querySelectorAll(".lk").forEach(c=>c.onclick=()=>{const j=db.lavori.find(x=>x.id===c.dataset.job);if(j)openJob(j)});
}
$("#btnJobNote").onclick=()=>{const j=editJob;$("#dJob").close();openNote(null,{cliente:j?.cliente,lavoro:j?.id})};

'''
def patch(s):
    def rep(old,new,cnt=1):
        nonlocal s
        assert s.count(old)==cnt,(old[:70],s.count(old)); s=s.replace(old,new)
    # --- numero fattura ---
    rep('<label>Data fattura<input type="date" id="jInv"></label>','<label>N° fattura<input id="jNum" placeholder="es. 12/2026"></label>\n      <label>Data fattura<input type="date" id="jInv"></label>')
    rep('$("#jInv").value=j?.dataFattura||"";','$("#jInv").value=j?.dataFattura||"";$("#jNum").value=j?.numFattura||"";')
    rep('dataFattura:$("#jInv").value,','dataFattura:$("#jInv").value,numFattura:$("#jNum").value.trim(),')
    rep('(j.descrizione+" "+cliName(j.cliente)+" "+(j.note||""))','(j.descrizione+" "+cliName(j.cliente)+" "+(j.note||"")+" "+(j.numFattura||""))',2)
    rep('<td class="num">${j.importo?eur(j.importo):""}</td>','<td class="num">${j.importo?eur(j.importo):""}${j.numFattura?`<div class="hint">Fatt. ${esc(j.numFattura)}</div>`:""}</td>')
    rep('${j.importo?`<b>${eur(j.importo)}</b>`:""}</div>','${j.importo?`<b>${eur(j.importo)}${j.numFattura?` <span class="hint" style="font-weight:400">· Fatt. ${esc(j.numFattura)}</span>`:""}</b>`:""}</div>')
    rep('<td class="num">${eur(j.importo)}</td>','<td class="num">${eur(j.importo)}${j.numFattura?`<div class="hint">Fatt. ${esc(j.numFattura)}</div>`:""}</td>')
    # --- appunti: dati e sincronizzazione ---
    rep('d.utenti??=[];','d.utenti??=[];d.appunti??=[];')
    rep('["clienti","lavori","utenti"]','["clienti","lavori","utenti","appunti"]',2)
    rep('const rem={clienti:[],lavori:[],utenti:[],eliminati:{}}','const rem={clienti:[],lavori:[],utenti:[],appunti:[],eliminati:{}}')
    # --- appunti: interfaccia ---
    rep('<button data-tab="lavori" class="on">I miei lavori</button>','<button data-tab="lavori" class="on">I miei lavori</button><button data-tab="appunti">Appunti</button>')
    rep('$("#tab-lavori").hidden=tab==="clienti"||tab==="archivio";','$("#tab-lavori").hidden=tab==="clienti"||tab==="archivio"||tab==="appunti";$("#tab-appunti").hidden=tab!=="appunti";')
    rep('  <section id="tab-clienti" hidden>',SECTION)
    rep('<dialog id="dJob">',DIALOG)
    rep('#btnNewJob,#btnNewCli{position:fixed','#btnNewJob,#btnNewCli,#btnNewNote{position:fixed')
    rep('.bar #q,.bar #qc,.bar #qa{','.bar #q,.bar #qc,.bar #qa,.bar #qn{')
    rep('</style>',CSS+'</style>')
    rep('renderClients();renderArchive()}','renderClients();renderArchive();renderNotes()}')
    rep('/* ---------- Clienti ---------- */',JS+'/* ---------- Clienti ---------- */')
    # pulsante "+ Appunto" nella scheda lavoro
    rep('<button type="button" class="b d" id="btnDelJob"','<button type="button" class="b" id="btnJobNote" title="Nuovo appunto collegato a questo lavoro">📝 Appunto</button><button type="button" class="b d" id="btnDelJob"')
    rep('$("#btnDelJob").style.visibility=j?"visible":"hidden";','$("#btnDelJob").style.visibility=j?"visible":"hidden";$("#btnJobNote").style.display=j?"":"none";')
    return s
if __name__=="__main__":
    for p in sys.argv[1:]:
        s=open(p,encoding='utf8').read();open(p,'w',encoding='utf8').write(patch(s));print("ok",p)
