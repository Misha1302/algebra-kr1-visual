"use strict";
/* Chapter 7: demonstrate LU, rank factorization and continuant recurrence.
 * All matrices and answers are fixed or computed from explicitly selected presets.
 * This script does NOT mark a chapter mastered or treat a quiz as a learning outcome.
 */
(() => {
  const section = document.getElementById("chapter-6");
  if (!section) return;
  const get = id => document.getElementById(id);
  const sub = n => String(n).split("").map(x => "₀₁₂₃₄₅₆₇₈₉"[Number(x)]).join("");
  const signed = n => String(n).replace(/-/g, "−");

  function matrix(rows, captionText, highlights = [], found = []) {
    const table = document.createElement("table");
    table.className = "ch7-matrix";
    const cap = document.createElement("caption");
    cap.textContent = captionText;
    table.append(cap);
    const tbody = document.createElement("tbody");
    rows.forEach((row, i) => {
      const tr = document.createElement("tr");
      row.forEach((value, j) => {
        const td = document.createElement("td");
        td.textContent = signed(value);
        if (value === 0) td.classList.add("ch7-zero");
        if (highlights.some(([r,c]) => r === i && c === j)) td.classList.add("ch7-highlight");
        if (found.some(([r,c]) => r === i && c === j)) td.classList.add("ch7-found");
        tr.append(td);
      });
      tbody.append(tr);
    });
    table.append(tbody);
    return table;
  }

  // We show the step that produces every number, not just the final factorization.
  const lu = [
    {
      rows:[[2,1],[4,5]], caption:"A · исходная", marked:[[1,0]],
      explanation:"Цель: убрать число 4 под двойкой. Мы имеем право заменить вторую строку, вычтя из неё кратную первой, но обязаны изменять все элементы этой строки."
    },
    {
      rows:[[2,1],[4,5]], caption:"A · ищем множитель k", marked:[[0,0],[1,0]],
      explanation:"Найдём k из уравнения 4 − k·2 = 0. Получаем k = 4/2 = 2. Теперь вычтем удвоенную первую строку из второй."
    },
    {
      rows:[[2,1],[0,3]], caption:"U · результат исключения", found:[[1,0],[1,1]],
      explanation:"R₂ ← (4,5) − 2·(2,1) = (4−4, 5−2) = (0,3). Это U: ниже главной диагонали появился ноль."
    },
    {
      rows:[[1,0],[2,1]], caption:"L · сохраняем множитель", found:[[1,0]],
      explanation:"В L на диагонали ставим единицы; выше диагонали — ноль; под диагональю записываем k=2. Проверка: L·U=[[2,1],[4,5]]=A. В L запоминается множитель до вычитания, а не знак «минус» из самой операции."
    }
  ];
  let luIndex = 0;
  function renderLU() {
    const state = lu[luIndex];
    get("ch7-lu-count").textContent = "Шаг " + (luIndex+1) + " из " + lu.length;
    get("ch7-lu-matrix").replaceChildren(matrix(state.rows,state.caption,state.marked||[],state.found||[]));
    get("ch7-lu-reason").textContent = state.explanation;
    get("ch7-lu-prev").disabled = luIndex===0;
    get("ch7-lu-next").disabled = luIndex===lu.length-1;
    get("ch7-lu-next").textContent = luIndex===lu.length-1?"Цепочка завершена":"Следующий шаг →";
  }
  get("ch7-lu-prev").addEventListener("click",()=>{luIndex=Math.max(0,luIndex-1);renderLU();});
  get("ch7-lu-next").addEventListener("click",()=>{luIndex=Math.min(lu.length-1,luIndex+1);renderLU();});
  get("ch7-lu-reset").addEventListener("click",()=>{luIndex=0;renderLU();});
  renderLU();

  const skeleton = [
    "1-й столбец A: коэффициенты (1,0). Берём 1·(1,2)+0·(2,5)=(1,2). Это первый столбец исходной A.",
    "2-й столбец A: коэффициенты (0,1). Берём 0·(1,2)+1·(2,5)=(2,5). Это второй столбец исходной A.",
    "3-й столбец A: коэффициенты (1,1). Берём 1·(1,2)+1·(2,5)=(1+2,2+5)=(3,7). Это третий столбец исходной A."
  ];
  const buttons = [...section.querySelectorAll("[data-ch7-column]")];
  function renderSkeleton(index) {
    buttons.forEach(btn=>btn.setAttribute("aria-pressed",String(Number(btn.dataset.ch7Column)===index)));
    get("ch7-skeleton-explain").textContent=skeleton[index];
  }
  buttons.forEach(btn=>btn.addEventListener("click",()=>renderSkeleton(Number(btn.dataset.ch7Column))));
  renderSkeleton(0);

  const presets = {
    base:{a:5,b:2,c:3},
    second:{a:4,b:1,c:2}
  };
  function recurrence(a,b,c,n) {
    if (![a,b,c,n].every(Number.isSafeInteger)||n<0||n>12)throw Error("Invalid recurrence arguments");
    const D=[1,a];
    for(let i=2;i<=n;i++)D.push(a*D[i-1]-b*c*D[i-2]);
    return D;
  }
  function tridiagonal(a,b,c,n) {
    return Array.from({length:n},(_,i)=>
      Array.from({length:n},(_,j)=>i===j?a:j===i+1?b:i===j+1?c:0));
  }
  function renderRecurrence() {
    const preset=presets[get("ch7-rec-preset").value];
    const n=Number(get("ch7-rec-n").value);
    if(!preset||!Number.isSafeInteger(n)||n<2||n>6)return;
    const {a,b,c}=preset;
    const D=recurrence(a,b,c,n);
    get("ch7-rec-n-value").textContent=n+"×"+n;
    get("ch7-rec-initial").textContent="Начальные: D₀=1, D₁="+a+".";
    get("ch7-rec-prev").textContent="Уже вычислены: D"+sub(n-2)+"="+D[n-2]+", D"+sub(n-1)+"="+D[n-1]+".";
    get("ch7-rec-equation").textContent="D"+sub(n)+" = "+a+"·"+signed(D[n-1])+" − "+(b*c)+"·"+signed(D[n-2])+" = "+signed(D[n])+".";
    get("ch7-rec-caption").textContent="Для порядка "+n+" используются только два предыдущих определителя; произведение bc="+(b*c)+".";
    get("ch7-rec-matrix").replaceChildren(matrix(tridiagonal(a,b,c,n),"Матрица "+n+"×"+n));
  }
  get("ch7-rec-preset").addEventListener("change",renderRecurrence);
  get("ch7-rec-n").addEventListener("input",renderRecurrence);
  renderRecurrence();

  function strictInteger(id) {
    // A numerical answer may be written as 2, 2.0 or 6/3.
    // Convert fractions exactly; do not coerce empty input to zero.
    const raw=get(id).value.trim().replace(/−/g,"-").replace(",",".").replace(/\s+/g,"");
    if(raw.length>48)return null;
    let numerator,denominator;
    const frac=/^([+-]?\d+)\/([+-]?\d+)$/.exec(raw);
    const decimal=/^([+-]?)(\d+)\.(\d+)$/.exec(raw);
    try {
      if(frac){
        numerator=BigInt(frac[1]);denominator=BigInt(frac[2]);
      } else if(decimal){
        numerator=BigInt((decimal[1]==="-"?"-":"")+decimal[2]+decimal[3]);
        denominator=10n**BigInt(decimal[3].length);
      } else if(/^[+-]?\d+$/.test(raw)){
        numerator=BigInt(raw);denominator=1n;
      } else return null;
      if(denominator===0n || numerator%denominator!==0n)return null;
      const result=Number(numerator/denominator);
      return Number.isSafeInteger(result)?result:null;
    } catch(_) {return null;}
  }
  function exercise(buttonId,ids,values,good,bad) {
    get(buttonId).addEventListener("click",()=>{
      const checks=ids.map((id,i)=>strictInteger(id)===values[i]);
      ids.forEach((id,i)=>get(id).setAttribute("aria-invalid",String(!checks[i])));
      const output=get(buttonId.replace("-check","-feedback"));
      const correct=checks.every(Boolean);
      output.hidden=false;
      output.classList.toggle("ch7-error",!correct);
      output.textContent=correct?good:bad(checks);
    });
  }
  exercise("ch7-lu-check",["ch7-lu-k","ch7-lu-u22"],[2,3],
    "Оба шага верны. k=6/3=2; новая строка (6,5)−2·(3,1)=(0,3). Значит, U₂₂=3.",
    checks=>checks[0]?"Множитель найден верно. Теперь вычти 2·1 также из числа 5, не только из 6.":"Начни с 6−k·3=0. Пустое поле или нечисловой ответ нельзя считать нулём.");
  exercise("ch7-sk-check",["ch7-sk-a","ch7-sk-b"],[2,3],
    "Верно: α=2, β=3, и 2·(1,2)+3·(1,3)=(5,13). Эти коэффициенты заполнят третий столбец C.",
    checks=>checks[0]?"Проверь вторую координату: 2α+3β=13.":"Составь оба уравнения: α+β=5 и 2α+3β=13. Вычти удвоенное первое из второго.");
  exercise("ch7-rec-check",["ch7-rec-d2","ch7-rec-d3"],[14,48],
    "Верно: D₂=4·4−2·1=14, затем D₃=4·14−2·4=48. Для D₄ получится 164.",
    checks=>checks[0]?"D₂ верен. Теперь используй D₃=4D₂−2D₁ и D₁=4.":"Сначала вычисли bc=1·2 и подставь D₀=1, D₁=4 в D₂=4D₁−bc·D₀.");
  window.__chapter7Math={
    recurrence,tridiagonal,luStages:lu.map(x=>x.rows.map(row=>row.slice())),
    skeletonCoefficients:[[1,0],[0,1],[1,1]],
    officialLU:{L:[[1,0,0],[0,1,0],[1,-2,1]],U:[[1,2,-3],[0,1,2],[0,0,11]]},
    officialSkeleton:{
      B:[[6,3],[6,3],[2,5],[-2,-5]],
      C:[[1,0,-0.5],[0,1,1]]
    }
  };
})();