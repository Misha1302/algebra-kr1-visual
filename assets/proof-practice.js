"use strict";
(() => {
  const prefix="algebra-kr1-proof-draft-v1:";
  document.querySelectorAll(".proof-workshop").forEach(section => {
    const id=section.dataset.proof;
    section.querySelectorAll(".proof-question").forEach(question=>{
      const answer=Number(question.dataset.answer);
      const feedback=question.querySelector(".proof-feedback");
      const options=[...question.querySelectorAll("button[data-option]")];
      options.forEach(button=>button.addEventListener("click",()=>{
        const index=Number(button.dataset.option),correct=index===answer;
        options.forEach(x=>x.setAttribute("aria-pressed",String(x===button)));
        feedback.hidden=false;
        feedback.classList.toggle("error",!correct);
        feedback.textContent=(correct?"Верно. ":"Попробуй ещё раз: выбранное обоснование недостаточно. ")+
          (correct?question.dataset.explanation:"Найди нужную предпосылку выше и проверь логический переход.");
      }));
    });
    const area=section.querySelector("textarea");
    if(!area)return;
    try {area.value=localStorage.getItem(prefix+id)||"";} catch (_) {}
    area.addEventListener("change",()=>{try{localStorage.setItem(prefix+id,area.value);}catch(_){}});
  });
})();