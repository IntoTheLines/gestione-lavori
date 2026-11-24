# Popup "incassi per mese" sul riquadro Da incassare. Uso: python3 feature_mesi_patch.py file...
import sys
CSS=r'''
/* ----- popup incassi per mese ----- */
.sum div.sinc{position:relative;cursor:default}
.mpop{display:none;position:absolute;top:calc(100% + 8px);left:0;z-index:30;background:var(--card);border:1px solid var(--line);border-radius:10px;
  box-shadow:0 12px 36px rgba(0,0,0,.16);padding:12px 14px;min-width:380px;max-height:70vh;overflow:auto;cursor:default}
.sinc:hover .mpop,.sinc.open .mpop{display:block}
.mpop h4{margin:0 0 2px;font-size:14px}.mpop .hint{display:block;margin-bottom:8px}
.mpop table{border:0;border-radius:0;font-size:13px}.mpop th,.mpop td{padding:5px 8px;border-bottom:1px solid var(--line);white-space:nowrap}
.mpop th{cursor:default;background:none}.mpop td.num{text-align:right}.mpop tr.tot td{font-weight:700;border-bottom:0}
.mpop .lt{color:var(--red)}.mpop .cur td{background:#f7f6ff}
@media (max-width:900px){.sinc{cursor:pointer}.sinc:hover .mpop{display:none}.sinc.open .mpop{display:block}
  .mpop{position:fixed;left:8px;right:8px;top:auto;bottom:calc(76px + env(safe-area-inset-bottom));min-width:0;max-height:60vh}}
'''
JS=r'''
  // popup incassi per mese (passa il mouse; sul telefono tocca il riquadro)
  {const all=db.lavori.filter(j=>!scope||utOf(j)===scope),mesi={},ym=d=>d?d.slice(0,7):"";
   const cur=today().slice(0,7);
   for(const j of all){const imp=+j.importo||0,inc=Math.min(+j.incassato||0,imp||Infinity);
     if(pagStato(j)!==2&&imp>0){const m=ym(scadOf(j)||j.consegna)||"zz";(mesi[m]??={p:0,i:0}).p+=imp-(+j.incassato||0)}
     if(inc>0&&j.dataPagamento){const m=ym(j.dataPagamento);(mesi[m]??={p:0,i:0}).i+=inc}}
   const lim=(()=>{const d=new Date();d.setMonth(d.getMonth()-11);return d.toISOString().slice(0,7)})();
   const keys=Object.keys(mesi).filter(m=>m==="zz"||m>=lim||mesi[m].p>0).sort();
   const nm=m=>m==="zz"?"Senza data":new Date(m+"-15").toLocaleDateString("it-IT",{month:"long",year:"numeric"});
   let tp=0,ti=0;const rows=keys.map(m=>{const r=mesi[m];tp+=r.p;ti+=r.i;const late=m!=="zz"&&m<cur&&r.p>0;
     return `<tr class="${m===cur?"cur":""}"><td>${nm(m)}${m===cur?" <span class='hint' style='display:inline'>(questo mese)</span>":""}</td>
       <td class="num ${late?"lt":""}">${r.p?eur(r.p)+(late?" ⚠":""):"—"}</td><td class="num">${r.i?eur(r.i):"—"}</td></tr>`}).join("");
   const box=$("#summary").children[2];box.classList.add("sinc");
   box.insertAdjacentHTML("beforeend",`<div class="mpop" onclick="event.stopPropagation()"><h4>Incassi per mese</h4>
     <span class="hint">Da incassare: mese di scadenza del pagamento (se manca, della consegna). Incassato: mese in cui è stato pagato (ultimi 12 mesi).</span>
     ${keys.length?`<table><thead><tr><th>Mese</th><th style="text-align:right">Da incassare</th><th style="text-align:right">Incassato</th></tr></thead><tbody>${rows}
     <tr class="tot"><td>Totale</td><td class="num">${eur(tp)}</td><td class="num">${eur(ti)}</td></tr></tbody></table>`:'<span class="hint">Nessun importo ancora.</span>'}</div>`);
   box.onclick=e=>{if(e.target.closest("#netto"))return;box.classList.toggle("open")};}
'''
def patch(s):
    def rep(old,new):
        nonlocal s
        assert s.count(old)==1,old[:60]; s=s.replace(old,new)
    rep('</style>',CSS+'</style>')
    rep('  $("#netto").onclick=()=>{',JS.lstrip("\n")+'  $("#netto").onclick=()=>{')
    return s
if __name__=="__main__":
    for p in sys.argv[1:]:
        s=open(p,encoding='utf8').read();open(p,'w',encoding='utf8').write(patch(s));print("ok",p)
