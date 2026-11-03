"use strict";
/* Transfer practice — fixed unseen examples with exact integer/rational checks.
   Achievements mean only a correctly verified exercise, never academic readiness. */
(() => {
  const BANK=window.AlgebraTransferBank;
  if(!BANK) throw new Error("Не найден набор самостоятельных задач.");
  const TOPICS=["matrix","gauss","permutations","det","inverse","rank","systems","advanced"];
  const TITLES={
    matrix:"Матрицы и индексы",gauss:"Метод Гаусса",permutations:"Подстановки слева направо",det:"Определители и знаки",
    inverse:"Обратная матрица и дополнения",rank:"Ранг и зависимость",
    systems:"СЛАУ и Кронекер — Капелли",advanced:"LU, скелет и рекурсии"
  };
  const KEY="algebra-kr1-independent-verified-v1";
  let completed={};
  try{const value=JSON.parse(localStorage.getItem(KEY)||"{}"); if(value&&typeof value==="object")completed=value;}catch(_){}
  function esc(s){return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
  function fraction(s){
    const v=String(s).trim().replace(/−/g,"-").replace(/\s+/g,"");
    const m=/^([+-]?\d+)(?:\/([+-]?\d+))?$/.exec(v);
    if(!m)return null;
    try{
      const num=BigInt(m[1]),den=BigInt(m[2]||"1");
      return den===0n?null:[num,den];
    }catch(_){return null;}
  }
  function matches(input,field){
    if(field.type==="choice")return input===field.answer;
    if(field.type==="text")return String(input).replace(/[()\s]/g,"")===field.answer;
    const a=fraction(input),b=fraction(field.answer);
    return a!==null&&b!==null&&a[0]*b[1]===b[0]*a[1];
  }
  function visualHTML(c){
    const v=c.visual;
    if(v.equations){
      return '<div class="transfer-equations" aria-label="Условия на числах">'+v.equations.map(e=>'<div>'+esc(e)+'</div>').join("")+'</div>';
    }
    let html='<div class="transfer-matrices">';
    for(const [name,rows] of Object.entries(v)){
      const table=rows.map(row=>'<tr>'+row.map(value=>'<td>'+esc(value)+'</td>').join("")+'</tr>').join("");
      html+='<table class="transfer-matrix"><caption>Матрица '+esc(name)+', '+rows.length+'×'+rows[0].length+'</caption><tbody>'+table+'</tbody></table>';
    }
    return html+'</div>';
  }
  function fieldsHTML(c,prefix){
    return c.fields.map(f=>{
      const id=prefix+'-'+c.id+'-'+f.id;
      let control='';
      if(f.type==="choice"){
        control='<select id="'+esc(id)+'" data-field="'+esc(f.id)+'"><option value="">Выбери ответ</option>'+
          f.options.map(([val,label])=>'<option value="'+esc(val)+'">'+esc(label)+'</option>').join('')+'</select>';
      } else {
        control='<input id="'+esc(id)+'" type="text" inputmode="decimal" autocomplete="off" data-field="'+esc(f.id)+'" placeholder="'+(f.type==="text"?"3,2":"целое или p/q")+'">';
      }
      return '<div class="transfer-field"><label for="'+esc(id)+'">'+esc(f.label)+'</label>'+control+
          '<p class="transfer-field-feedback" role="status" hidden></p></div>';
    }).join("");
  }
  function progress(){
    const n=TOPICS.filter(t=>Array.isArray(completed[t])&&completed[t].length>0).length;
    const label=document.getElementById("transfer-progress");
    if(label)label.textContent=n+"/8";
    document.querySelectorAll("[data-independent-progress]").forEach(e=>
      e.textContent=n+"/8 тем с хотя бы одной проверенной задачей (это не готовность к КР).");
  }
  function markCorrect(topic,caseId){
    if(!Array.isArray(completed[topic]))completed[topic]=[];
    if(!completed[topic].includes(caseId))completed[topic].push(caseId);
    try{localStorage.setItem(KEY,JSON.stringify(completed));}catch(_){}
    progress();
  }
  function score(root,c){
    const fields=c.fields.map(f=>{
      const element=root.querySelector('[data-field="'+f.id+'"]');
      const actual=element.value.trim();
      const ok=matches(actual,f);
      return {field:f,element,actual,ok};
    });
    return {fields,all:fields.every(x=>x.ok)};
  }
  function topicMount(slot){
    const topic=slot.dataset.transfer;
    if(!TOPICS.includes(topic))return;
    let index=0;
    const show=()=>{
      const variants=BANK[topic],c=variants[index];
      slot.innerHTML=
        '<div class="transfer-heading"><span>САМОСТОЯТЕЛЬНЫЙ ПЕРЕНОС НАВЫКА · '+esc(TITLES[topic])+'</span>'+
        '<span>Вариант '+(index+1)+' из '+variants.length+'</span></div>'+
        '<h3>'+esc(c.title)+'</h3><p class="transfer-task">'+esc(c.task)+'</p>'+
        visualHTML(c)+
        '<div class="transfer-fields">'+fieldsHTML(c,"lesson-"+topic)+'</div>'+
        '<div class="transfer-actions"><button type="button" class="transfer-check">Проверить вычисления</button>'+
        '<button type="button" class="transfer-next">Другой вариант</button></div>'+
        '<p class="transfer-status" role="status" aria-live="polite"></p>'+
        '<details class="transfer-hint"><summary>Направляющая подсказка (по запросу)</summary><p>'+esc(c.hint)+'</p></details>'+
        '<details class="transfer-answer"><summary>Пошаговая сверка после самостоятельной попытки</summary><p>'+esc(c.reason)+'</p></details>'+
        '<p class="transfer-disclaimer">Проверяются конкретные числа и выбор метода. Правильный вариант не означает, что все темы КР освоены. Дробь вводи точно как p/q.</p>';
      const status=slot.querySelector('.transfer-status');
      slot.querySelector(".transfer-check").addEventListener("click",()=>{
        const state=score(slot,c);
        state.fields.forEach(({field,element,actual,ok})=>{
          element.setAttribute("aria-invalid",String(!ok));
          const note=element.parentElement.querySelector(".transfer-field-feedback");
          note.hidden=ok;
          note.textContent=ok?"":"Проверь этот шаг. "+field.hint+(actual===""?" Поле пока пустое.":"");
        });
        status.classList.toggle("is-error",!state.all);
        if(state.all){
          status.textContent="Все проверяемые шаги верны. Сверь самостоятельное объяснение с разбором ниже.";
          markCorrect(topic,c.id);
        } else {
          const count=state.fields.filter(x=>x.ok).length;
          status.textContent="Верно "+count+" из "+state.fields.length+" шагов. Исправь выделенные поля, затем проверь ещё раз.";
        }
      });
      slot.querySelector(".transfer-next").addEventListener("click",()=>{
        index=(index+1)%variants.length;
        show();
      });
    };
    show();
  }
  // Insert on the 7-chapter course and use the same bank on the standalone training page.
  const chapters=document.querySelectorAll("section.chapter");
  if(chapters.length===7){
    chapters.forEach((ch,i)=>{
      const slot=document.createElement("section");
      slot.className="transfer-practice";
      const chapterTopics=["matrix","gauss","det","inverse","rank","systems","advanced"];
      slot.dataset.transfer=chapterTopics[i];
      slot.id="try-"+chapterTopics[i];
      const next=ch.querySelector(".chapter-next");
      if(next)next.before(slot);else ch.append(slot);
      if(i===2){
        const extra=document.createElement("section");
        extra.className="transfer-practice";
        extra.dataset.transfer="permutations";
        extra.id="try-permutations";
        slot.after(extra);
      }
    });
  }
  document.querySelectorAll(".transfer-practice[data-transfer]").forEach(topicMount);
  progress();
  window.AlgebraTransfer={bank:BANK,topics:TOPICS,titles:TITLES,fieldsHTML,visualHTML,matches,score,progress};
})();