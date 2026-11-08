const fs=require('fs');
const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,WidthType,ShadingType,AlignmentType,BorderStyle,Footer,PageNumber,LineRuleType}=require('docx');
const ACC="8A1C1C", INK="1A1A1A", GREY="6B6B6B", RULE="C9C2B8", TINT="F4EFE8";
const BODY="Cambria", SANS="Arial";
function runs(text,base={}){ // **bold** and *italic*
  const out=[]; const re=/(\*\*[^*]+\*\*|\*[^*]+\*)/g; let last=0,m;
  while((m=re.exec(text))){ if(m.index>last) out.push(new TextRun({text:text.slice(last,m.index),...base}));
    const t=m[0]; if(t.startsWith('**')) out.push(new TextRun({text:t.slice(2,-2),bold:true,...base})); else out.push(new TextRun({text:t.slice(1,-1),italics:true,...base})); last=m.index+t.length;}
  if(last<text.length) out.push(new TextRun({text:text.slice(last),...base})); return out;}
const W=9026; // A4 width minus 1" margins (11906-2*1440)
function table(rows){
  const cells=rows.map(r=>r.replace(/^\||\|$/g,'').split('|').map(c=>c.trim()));
  const hdr=cells[0], body=cells.slice(2); const n=hdr.length;
  const widths=n===2?[Math.round(W*0.55),W-Math.round(W*0.55)]:[Math.round(W*0.2),Math.round(W*0.4),W-Math.round(W*0.2)-Math.round(W*0.4)];
  const b={style:BorderStyle.SINGLE,size:4,color:RULE}, none={style:BorderStyle.NONE,size:0,color:"FFFFFF"};
  const mk=(txt,i,isH)=>new TableCell({width:{size:widths[i],type:WidthType.DXA},
    shading:isH?{type:ShadingType.CLEAR,fill:ACC,color:"auto"}:undefined,
    margins:{top:80,bottom:80,left:120,right:120},
    borders:{top:isH?none:b,bottom:b,left:none,right:none},
    children:[new Paragraph({spacing:{before:0,after:0},children:runs(txt,{font:SANS,size:18,color:isH?"FFFFFF":INK,bold:isH})})]});
  return new Table({width:{size:W,type:WidthType.DXA},columnWidths:widths,
    rows:[new TableRow({tableHeader:true,children:hdr.map((t,i)=>mk(t,i,true))}),...body.map(r=>new TableRow({children:r.map((t,i)=>mk(t,i,false))}))]});
}
function build(md,kicker){
  const L=md.split('\n'); const kids=[]; let i=0; let seenBody=false;
  kids.push(new Paragraph({spacing:{after:120},children:[new TextRun({text:kicker,font:SANS,size:16,bold:true,color:ACC,characterSpacing:40})]}));
  while(i<L.length){ const l=L[i];
    if(!l.trim()){i++;continue;}
    if(l.startsWith('# ')){ kids.push(new Paragraph({spacing:{after:200,line:300,lineRule:LineRuleType.AUTO},children:[new TextRun({text:l.slice(2),font:BODY,size:52,bold:true,color:INK})]})); i++; continue;}
    if(l.startsWith('## ')){ kids.push(new Paragraph({keepNext:true,spacing:{before:320,after:120},children:[new TextRun({text:l.slice(3),font:SANS,size:24,bold:true,color:ACC})]})); i++; continue;}
    if(l.startsWith('>')){ const q=[]; while(i<L.length&&L[i].startsWith('>')) q.push(L[i++].replace(/^>\s?/,''));
      const bd={left:{style:BorderStyle.SINGLE,size:24,color:ACC,space:8}};
      q.forEach((s,k)=>{ const isHead=k===0&&!s.startsWith('- '); const txt=s.replace(/^- /,'');
        kids.push(new Paragraph({border:bd,shading:{type:ShadingType.CLEAR,fill:'F7F1F0',color:'auto'},indent:{left:160,right:160},spacing:{before:k===0?200:0,after:k===q.length-1?280:80,line:290,lineRule:LineRuleType.AUTO},
          children:isHead?[new TextRun({text:txt.toUpperCase(),font:SANS,size:16,bold:true,color:ACC,characterSpacing:30})]:[new TextRun({text:'■  ',font:SANS,size:14,color:ACC}),...runs(txt,{font:SANS,size:19,color:INK})]})); });
      continue;}
    if(l.startsWith('|')){ const rows=[]; while(i<L.length&&L[i].startsWith('|')) rows.push(L[i++]); kids.push(new Paragraph({spacing:{before:120,after:0},children:[]})); kids.push(table(rows)); continue;}
    if(/^\*\*[^*]+\*\*$/.test(l.trim())){ // byline
      kids.push(new Paragraph({spacing:{before:120,after:240},border:{bottom:{style:BorderStyle.SINGLE,size:6,color:RULE,space:8}},children:[new TextRun({text:l.trim().slice(2,-2).toUpperCase(),font:SANS,size:18,bold:true,color:GREY,characterSpacing:30})]})); i++; continue;}
    if(/^\*[^*].*\*$/.test(l.trim())){ const t=l.trim().slice(1,-1);
      if(t.startsWith('Nguồn')){ kids.push(new Paragraph({spacing:{before:60,after:240},children:[new TextRun({text:t,font:SANS,size:16,italics:true,color:GREY})]})); }
      else { kids.push(new Paragraph({spacing:{after:200,line:320,lineRule:LineRuleType.AUTO},children:[new TextRun({text:t,font:BODY,size:26,italics:true,color:"3A3A3A"})]})); }
      i++; continue;}
    const first=!seenBody; seenBody=true;
    const rr=runs(l,{font:BODY,size:22,color:INK});
    if(first){ const t=l; kids.push(new Paragraph({alignment:AlignmentType.JUSTIFIED,spacing:{after:160,line:330,lineRule:LineRuleType.AUTO},children:[new TextRun({text:t.charAt(0),font:BODY,size:40,bold:true,color:ACC}),new TextRun({text:t.slice(1),font:BODY,size:22,color:INK})]})); }
    else kids.push(new Paragraph({alignment:AlignmentType.JUSTIFIED,spacing:{after:160,line:330,lineRule:LineRuleType.AUTO},children:rr}));
    i++; }
  kids.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:240},children:[new TextRun({text:"■",font:SANS,size:16,color:ACC})]}));
  return new Document({creator:"Đinh Trần Tuấn Linh",styles:{default:{document:{run:{font:BODY,size:22}}}},
    sections:[{properties:{page:{size:{width:11906,height:16838},margin:{top:1440,bottom:1300,left:1440,right:1440}}},
      footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,children:[new TextRun({children:[PageNumber.CURRENT],font:SANS,size:16,color:GREY})]})]})},
      children:kids}]});
}
// Một bài: node build_docx.js bai.md bai.docx ["DÒNG TRÊN TÍT"]
// Ba phương án (cách cũ): node build_docx.js <thu-muc-co-PA1.md...> <thu-muc-ra>
const [,,src,out,kick]=process.argv;
if(src.endsWith('.md')){
  (async()=>{const d=build(fs.readFileSync(src,'utf8'),kick||"GÓC NHÌN"); fs.writeFileSync(out,await Packer.toBuffer(d)); console.log(out);})();
} else {
const dir=src;
const jobs=[["PA1","GÓC NHÌN · CÔNG TY MỘT NGƯỜI","PA1-Trach-nhiem-huu-han-met-moi-vo-han.docx"],["PA2","GÓC NHÌN · CÔNG TY MỘT NGƯỜI","PA2-Cong-ty-mot-nguoi-sau-con-sot.docx"],["PA3","GÓC NHÌN · CÔNG TY MỘT NGƯỜI","PA3-Nha-cung-cap-tot-nhat-nam-sau.docx"]];
(async()=>{for(const [f,k,o] of jobs){const d=build(fs.readFileSync(`${dir}/${f}.md`,'utf8'),k); fs.writeFileSync(`${out}/${o}`,await Packer.toBuffer(d)); console.log(o);}})();
}
