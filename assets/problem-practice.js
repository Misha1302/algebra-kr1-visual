"use strict";
(() => {
  // Private draft storage: this is never a mathematical grade.
  const prefix="algebra-kr1-draft-v2:";
  document.querySelectorAll(".attempt-workspace").forEach(box => {
    const id=box.dataset.problem;
    const field=box.querySelector("textarea");
    const button=box.querySelector("[data-save-attempt]");
    const status=box.querySelector(".save-message");
    try {
      const stored=localStorage.getItem(prefix+id);
      if(stored!==null){field.value=stored;status.textContent="Ранее сохранённый черновик загружен.";}
    } catch (_) {status.textContent="Хранилище недоступно. Черновик остаётся в этом поле.";}
    button.addEventListener("click",()=>{
      try {
        localStorage.setItem(prefix+id,field.value);
        status.textContent="Черновик сохранён в браузере. Проверку ответа выполняй по эталону.";
      } catch (_) {status.textContent="Сохранить не удалось. Скопируй текст перед закрытием страницы.";}
    });
  });
  // Scrollable MathML expressions need keyboard focus for small-screen readers.
  function enableMathKeyboardScroll() {
    document.querySelectorAll('math[display="block"]').forEach(element=>{
      if(element.scrollWidth>element.clientWidth+1){
        element.setAttribute("tabindex","0");
        element.setAttribute("title","Выражение можно прокручивать стрелками по горизонтали");
      } else {
        element.removeAttribute("tabindex");
        element.removeAttribute("title");
      }
    });
  }
  enableMathKeyboardScroll();
  window.addEventListener("resize",enableMathKeyboardScroll);
})();