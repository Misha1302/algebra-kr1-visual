"use strict";
(() => {
  const app=window.AlgebraTransfer;
  const form=document.querySelector("#mock-exam");
  if(!form||!app)return;
  // Deterministic, repeatable test cases distinct from the first worked variant in each lesson.
  const variants=[1,2,2,0,1,2,0,1];
  const cases=app.topics.map((t,i)=>({...app.bank[t][variants[i]],topic:t}));
  cases.forEach((c,i)=>{
    const section=document.createElement("section");
    section.className="exam-case";
    section.id="exam-"+c.topic;
    section.innerHTML=
      '<span class="micro">Пункт '+(i+1)+' / '+cases.length+' · '+app.titles[c.topic]+'</span>'+
      '<h3>'+c.title+'</h3><p>'+c.task+'</p>'+app.visualHTML(c)+
      '<div class="transfer-fields">'+app.fieldsHTML(c,"exam")+'</div>'+
      '<div class="exam-after" hidden><strong>Разбор после завершения попытки:</strong> <span></span></div>';
    form.append(section);
  });
  const submit=document.createElement("button");
  submit.type="submit";submit.className="exam-submit";
  submit.textContent="Завершить попытку и открыть разборы";
  form.append(submit);
  form.addEventListener("submit",event=>{
    event.preventDefault();
    let correctCases=0,correctFields=0,totalFields=0;
    cases.forEach((c,i)=>{
      const sec=form.querySelector("#exam-"+c.topic);
      const result=app.score(sec,c);
      if(result.all)correctCases++;
      result.fields.forEach(({field,element,ok})=>{
        totalFields++;
        if(ok)correctFields++;
        element.setAttribute("aria-invalid",String(!ok));
        const msg=element.parentElement.querySelector(".transfer-field-feedback");
        msg.hidden=ok;
        msg.textContent=ok?"":"Проверка: "+field.hint;
      });
      const after=sec.querySelector(".exam-after");
      after.hidden=false;
      after.querySelector("span").textContent=c.reason;
    });
    const verdict=document.getElementById("exam-verdict");
    verdict.textContent="Проверяемые задания: "+correctCases+" из "+cases.length+
      " полностью верно; промежуточные шаги: "+correctFields+" из "+totalFields+
      ". Это диагностический результат, а не отметка готовности к КР. После разбора вернись к слабым темам.";
    submit.disabled=true;
    submit.textContent="Попытка завершена; объяснения открыты";
  });
})();