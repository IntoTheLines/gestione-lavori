# Esporta in PDF i lavori di un cliente (PDF generato in JS, senza librerie). Uso: python3 feature_pdf_patch.py file...
import sys
DIALOG=r'''<dialog id="dPdf">
  <form method="dialog" id="formPdf">
    <div class="dh">📄 Esporta lavori in PDF</div>
    <div class="db">
      <label class="full">Cliente<select id="pCli" required></select></label>
      <label>Consegna dal (facoltativo)<input type="date" id="pDal"></label>
      <label>al (facoltativo)<input type="date" id="pAl"></label>
      <label>Quali lavori<select id="pTipo"><option value="tutti">Tutti</option><option value="aperti">Solo da incassare</option><option value="pagati">Solo pagati</option></select></label>
      <label>Di chi<select id="pChi"><option value="tutti">Tutto il team</option><option value="miei">Solo i miei</option></select></label>
      <div class="full hint" id="pInfo"></div>
    </div>
    <div class="df"><div class="spacer"></div><button type="button" class="b" onclick="this.closest('dialog').close()">Annulla</button><button class="b p">Crea PDF</button></div>
  </form>
</dialog>

<dialog id="dCli">'''
JS=r'''/* ---------- Esporta PDF dei lavori di un cliente ---------- */
const HW=[278,278,355,556,556,889,667,191,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611,278,278,278,469,556,333,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500,334,260,334,584];
const pdfW=(s,sz,b)=>{let w=0;for(const ch of String(s)){const c=ch.charCodeAt(0);w+=(c>=32&&c<=126?HW[c-32]:556)}return w*sz/1000*(b?1.07:1)};
const pdfEsc=s=>{let o="";for(let ch of String(s)){let c=ch.charCodeAt(0);
  if(ch==="€")c=128;else if(c===8217||c===8216)c=39;else if(c===8220||c===8221)c=34;else if(c===8211||c===8212)c=45;else if(c===8230){o+="...";continue}else if(c>255)c=63;
  if(c===40||c===41||c===92)o+="\\"+String.fromCharCode(c);else if(c<32||c>126)o+="\\"+c.toString(8).padStart(3,"0");else o+=String.fromCharCode(c)}return o};
function pdfWrap(s,sz,max,b){const out=[];for(const para of String(s||"").split("\n")){let line="";
  for(const w of para.split(/\s+/)){const t=line?line+" "+w:w;if(pdfW(t,sz,b)<=max||!line)line=t;else{out.push(line);line=w}
    while(pdfW(line,sz,b)>max&&line.length>1){let k=line.length;while(k>1&&pdfW(line.slice(0,k),sz,b)>max)k--;out.push(line.slice(0,k));line=line.slice(k)}}
  out.push(line)}return out}
function pdfBuild(pages){ // pages = stream di contenuto; restituisce il PDF come stringa ASCII
  const o=[];const add=s=>{o.push(s);return o.length};
  add("<< /Type /Catalog /Pages 2 0 R >>");add("");
  add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>");
  add("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>");
  const kids=[];for(const c of pages){const ci=add(`<< /Length ${c.length} >>\nstream\n${c}\nendstream`);
    kids.push(add(`<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents ${ci} 0 R >>`))}
  o[1]=`<< /Type /Pages /Kids [${kids.map(k=>k+" 0 R").join(" ")}] /Count ${kids.length} >>`;
  let s="%PDF-1.4\n";const off=[];o.forEach((x,i)=>{off.push(s.length);s+=`${i+1} 0 obj\n${x}\nendobj\n`});
  const xr=s.length;s+=`xref\n0 ${o.length+1}\n0000000000 65535 f \n`+off.map(n=>String(n).padStart(10,"0")+" 00000 n \n").join("");
  return s+`trailer\n<< /Size ${o.length+1} /Root 1 0 R >>\nstartxref\n${xr}\n%%EOF\n`}
function pdfLavori(cid,list,opt){
  const M=40,W=515,cols=[{t:"Lavoro",w:190},{t:"N° fattura",w:78},{t:"Consegna",w:72},{t:"Pagato il",w:72},{t:"Importo",w:103,r:1}];
  const pages=[];let c="",y=0;
  const T=(x,yy,s,sz,b,col)=>{c+=`BT ${col?col+" rg ":""}/${b?"F2":"F1"} ${sz} Tf ${x.toFixed(1)} ${yy.toFixed(1)} Td (${pdfEsc(s)}) Tj ET\n`+(col?"0 g\n":"")};
  const TR=(xr,yy,s,sz,b)=>T(xr-pdfW(s,sz,b),yy,s,sz,b);
  const L=(x1,y1,x2,y2,g)=>{c+=`${g||0.85} G 0.6 w ${x1} ${y1.toFixed(1)} m ${x2} ${y2.toFixed(1)} l S\n`};
  const head=()=>{c+=`0.95 g ${M} ${(y-6).toFixed(1)} ${W} 20 re f 0 g\n`;let x=M+6;
    cols.forEach(k=>{k.r?TR(x+k.w-12,y,k.t,9,1):T(x,y,k.t,9,1);x+=k.w});y-=22};
  const newPage=first=>{if(c)pages.push(c);c="";y=800;
    T(M,y,"Gestione Lavori",9,0,"0.48 0.41 0.93");TR(M+W,y,"Generato il "+fmtD(today()),9);y-=26;
    if(first){T(M,y,"Lavori - "+cliName(cid),18,1);y-=18;T(M,y,opt.sub,10,0,"0.42 0.45 0.5");y-=26}
    head()};
  newPage(true);
  const fz=9.5;let tot=0,inc=0;
  for(const j of list){
    const lines=pdfWrap(j.descrizione,fz,cols[0].w-10,0);const h=lines.length*12+8;
    if(y-h<70){newPage(false)}
    let x=M+6;lines.forEach((l,i)=>T(x,y-i*12,l,fz));x+=cols[0].w;
    T(x,y,j.numFattura||"-",fz);x+=cols[1].w;T(x,y,j.consegna?fmtD(j.consegna):"-",fz);x+=cols[2].w;
    const pg=pagStato(j)===2;T(x,y,j.dataPagamento?fmtD(j.dataPagamento):(pg?"pagato":"-"),fz,0,!j.dataPagamento&&!pg?"0.6 0.62 0.65":"");x+=cols[3].w;
    TR(x+cols[4].w-12,y,j.importo!==""&&j.importo!=null?eur(j.importo):"-",fz,1);
    y-=h-6;L(M,y,M+W,y);y-=14;tot+=+j.importo||0;inc+=Math.min(+j.incassato||0,+j.importo||0)}
  if(!list.length){T(M+6,y,"Nessun lavoro per i criteri scelti.",10,0,"0.42 0.45 0.5");y-=20}
  if(y<120)newPage(false);
  y-=6;const rx=M+W-6,lx=M+W-230;
  [["Totale lavori",tot,1],["Incassato",inc,0],["Da incassare",tot-inc,1]].forEach(([k,v,b])=>{T(lx,y,k,10,b);TR(rx,y,eur(v),10,b);y-=16});
  pages.push(c);
  return pdfBuild(pages.map((p,i)=>p+`BT /F1 8 Tf 0.5 g ${M+W/2-20} 28 Td (${pdfEsc("Pagina "+(i+1)+" di "+pages.length)}) Tj ET\n`))}
async function savePdf(name,str){
  if(window.desktop&&desktop.pick&&!window.__mobileWeb){const p=await desktop.pick("pdf",name);if(!p)return;await desktop.write(p,str);
    if(desktop.open&&confirm("PDF salvato in:\n"+p+"\n\nAprirlo adesso?"))desktop.open(p);return}
  const blob=new Blob([Uint8Array.from(str,ch=>ch.charCodeAt(0))],{type:"application/pdf"});
  const file=new File([blob],name,{type:"application/pdf"});
  if(isNarrow()&&navigator.canShare&&navigator.canShare({files:[file]})){try{await navigator.share({files:[file],title:name});return}catch(e){if(e.name==="AbortError")return}}
  const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),30000)}
function pdfList(){const cid=$("#pCli").value,dal=$("#pDal").value,al=$("#pAl").value,tipo=$("#pTipo").value,chi=$("#pChi").value;
  return db.lavori.filter(j=>j.cliente===cid&&(chi==="tutti"||utOf(j)===me)&&(!dal||(j.consegna&&j.consegna>=dal))&&(!al||(j.consegna&&j.consegna<=al))
    &&(tipo==="tutti"||(tipo==="pagati"?pagStato(j)===2:pagStato(j)!==2&&pagStato(j)!==-1)))
    .sort((a,b)=>(a.consegna||"9999").localeCompare(b.consegna||"9999"))}
const pdfInfo=()=>{const n=pdfList().length;$("#pInfo").textContent=n?`${n} lavor${n===1?"o":"i"} nel PDF (anche quelli in Archivio), in ordine di consegna.`:"Nessun lavoro per questi criteri."};
function openPdf(cid){const cs=[...db.clienti].sort((a,b)=>a.nome.localeCompare(b.nome));
  $("#pCli").innerHTML=cs.map(c=>`<option value="${c.id}">${esc(c.nome)}</option>`).join("");if(cid)$("#pCli").value=cid;
  pdfInfo();$("#dPdf").showModal()}
["#pCli","#pDal","#pAl","#pTipo","#pChi"].forEach(s=>$(s).addEventListener("input",pdfInfo));
$("#formPdf").onsubmit=async e=>{e.preventDefault();const cid=$("#pCli").value;if(!cid)return;
  const dal=$("#pDal").value,al=$("#pAl").value,tipo=$("#pTipo").value;
  const sub=[dal||al?`Consegne ${dal?"dal "+fmtD(dal):""} ${al?"al "+fmtD(al):""}`.trim():"Tutti i periodi",
    {tutti:"tutti i lavori",aperti:"solo da incassare",pagati:"solo pagati"}[tipo]].join(" - ");
  const list=pdfList();const str=pdfLavori(cid,list,{sub:sub+` - ${list.length} lavor${list.length===1?"o":"i"}`});
  const nm=("Lavori "+cliName(cid)+" "+today()).replace(/[\\/:*?"<>|]+/g,"-")+".pdf";
  $("#dPdf").close();try{await savePdf(nm,str)}catch(err){alert("PDF non salvato: "+(err.message||err))}};
$("#btnPdf").onclick=()=>openPdf();
$("#btnCliPdf").onclick=()=>{const c=editCli;$("#dCli").close();openPdf(c?.id)};

'''
def patch(s):
    def rep(old,new,cnt=1):
        nonlocal s
        assert s.count(old)==cnt,(old[:70],s.count(old)); s=s.replace(old,new)
    rep('<dialog id="dCli">',DIALOG)
    rep('<button class="b p" id="btnNewCli">+ Nuovo cliente</button>','<button class="b p" id="btnNewCli">+ Nuovo cliente</button>\n      <button class="b" id="btnPdf">📄 Esporta PDF</button>')
    rep('''      <button type="button" class="b d" id="btnDelCli">Elimina</button>''','''      <button type="button" class="b d" id="btnDelCli">Elimina</button>\n      <button type="button" class="b" id="btnCliPdf">📄 PDF lavori</button>''')
    rep('$("#btnDelCli").style.visibility=c?"visible":"hidden";','$("#btnDelCli").style.visibility=c?"visible":"hidden";$("#btnCliPdf").style.display=c?"":"none";')
    rep('/* ---------- Clienti ---------- */',JS+'/* ---------- Clienti ---------- */')
    return s
if __name__=="__main__":
    for p in sys.argv[1:]:
        s=open(p,encoding='utf8').read();open(p,'w',encoding='utf8').write(patch(s));print("ok",p)
