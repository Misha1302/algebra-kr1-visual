"use strict";
(() => {
  const A=[[1,2,3],[0,4,5],[1,0,6]], $=id=>document.getElementById(id);
  const d2=(a,b,c,d)=>a*d-b*c;
  // Invalid/empty input is not mathematical zero. Never silently alter the example.
  function finiteValues(ids, errorId, integerIds=[]) {
    const values=[],bad=[];
    for(const id of ids){
      const input=$(id),raw=input.value.trim(),v=Number(raw);
      const min=input.min!==""?Number(input.min):-Infinity;
      const max=input.max!==""?Number(input.max):Infinity;
      const valid=raw!=="" && Number.isFinite(v) && v>=min && v<=max &&
        !input.validity.badInput && (!integerIds.includes(id)||Number.isInteger(v));
      input.setAttribute("aria-invalid",String(!valid));
      if(!valid)bad.push(id);
      values.push(v);
    }
    const message=$(errorId);
    message.hidden=bad.length===0;
    message.textContent=bad.length?
       "Проверь поля "+bad.join(", ")+": введи "+(integerIds.length?"допустимые числа (n — целое от 1 до 12).":"числа в указанном диапазоне.")+
       " Предыдущий корректный результат оставлен без изменений.":"";
    return bad.length?null:values;
  }
  const safe=x=>String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
  const sign=x=>x<0?"− "+Math.abs(x):"+ "+x;
  function matrix(arr,classes,click){
    classes=classes||(()=>""),click=click||false;
    return arr.map((row,i)=>row.map((v,j)=>click?
      '<button type="button" class="cell selectable '+classes(i,j)+'" data-i="'+i+'" data-j="'+j+'" aria-label="Элемент '+(i+1)+', '+(j+1)+'">'+safe(v)+'</button>':
      '<span class="cell '+classes(i,j)+'">'+safe(v)+'</span>').join("")).join("");
  }
  function det2(){
    const v=finiteValues(["a","b","c","d"],"det2-error");
    if(v===null)return;
    const r=d2(...v);
    $("det2-result").textContent=v[0]+"·"+v[3]+" − ("+v[1]+"·"+v[2]+") = "+(v[0]*v[3])+" − ("+(v[1]*v[2])+") = "+r;
    $("det2-meaning").textContent=r===0?"Определитель равен нулю: обратной матрицы нет.":"Определитель отличен от нуля: матрица обратима. Модуль определителя — коэффициент изменения площади.";
  }
  ["a","b","c","d"].forEach(id=>$(id).addEventListener("input",det2));
  $("det2-reset").addEventListener("click",()=>{["a","b","c","d"].forEach((id,i)=>$(id).value=[2,1,3,4][i]);det2()});
  $("det2-singular").addEventListener("click",()=>{["a","b","c","d"].forEach((id,i)=>$(id).value=[2,1,4,2][i]);det2()});
  det2();
  function minor(i,j){
    const m=A.filter((_,r)=>r!==i).map(row=>row.filter((_,c)=>c!==j));
    return {m:m,v:d2(m[0][0],m[0][1],m[1][0],m[1][1]),sgn:(i+j)%2?-1:1};
  }
  let axis="r0",step=0;
  function laplace(){
    const rowMode=axis[0]==="r",fix=+axis[1],i=rowMode?fix:step,j=rowMode?step:fix;
    const x=minor(i,j),v=A[i][j],contrib=v*x.sgn*x.v;
    $("mat3").innerHTML=matrix(A,(r,c)=>r===i&&c===j?"target":r===i||c===j?"removed":"",true);
    $("minor2").innerHTML=matrix(x.m);
    document.querySelectorAll("#mat3 button").forEach(b=>b.addEventListener("click",()=>{
      const r=+b.dataset.i,c=+b.dataset.j;
      axis="r"+r;step=c;$("expand-axis").value=axis;laplace();
    }));
    $("laplace-label").textContent="Выбрана "+(rowMode?"строка":"столбец")+" "+(fix+1)+"; шаг "+(step+1)+" из 3";
    const vals=x.m.flat();
    $("laplace-step").textContent="M"+(i+1)+(j+1)+" = "+vals[0]+"·"+vals[3]+" − "+vals[1]+"·"+vals[2]+" = "+x.v+
      "; C"+(i+1)+(j+1)+" = "+(x.sgn===-1?"−":"+")+"M"+(i+1)+(j+1)+" = "+(x.sgn*x.v)+"; вклад = "+v+"·("+(x.sgn*x.v)+") = "+contrib+".";
    const terms=[0,1,2].map(k=>{let r=rowMode?fix:k,c=rowMode?k:fix,q=minor(r,c);return A[r][c]*q.v*q.sgn});
    const sum=terms.reduce((a,b)=>a+b,0);
    $("laplace-total").textContent="Три вклада: "+terms.map((v,k)=>k===0?String(v):sign(v)).join(" ")+" = "+sum+
      ". Результат равен 22 при любом разложении.";
    $("lap-prev").disabled=step===0;$("lap-next").disabled=step===2;
  }
  $("expand-axis").addEventListener("change",e=>{axis=e.target.value;step=0;laplace()});
  $("lap-prev").addEventListener("click",()=>{step=Math.max(0,step-1);laplace()});
  $("lap-next").addEventListener("click",()=>{step=Math.min(2,step+1);laplace()});
  laplace();
  const permutations=[[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
  function inversions(p){let k=0;for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++)if(p[i]>p[j])k++;return k}
  let activePerm=0;
  $("perm-det-options").innerHTML=permutations.map((p,i)=>'<button type="button" class="btn" data-perm="'+i+'">'+p.map(x=>x+1).join(" ")+"</button>").join("");
  function leibniz(){
    const p=permutations[activePerm],inv=inversions(p),pr=p.reduce((acc,c,r)=>acc*A[r][c],1);
    $("perm-det-matrix").innerHTML=matrix(A,(r,c)=>p[r]===c?"target":"");
    $("perm-det-work").textContent="σ = ("+p.map(x=>x+1).join(", ")+"), инверсий: "+inv+", знак: "+(inv%2?"−":"+")+". Произведение: "+p.map((c,r)=>A[r][c]).join(" · ")+" = "+pr+". Вклад: "+(inv%2?-pr:pr)+".";
    document.querySelectorAll("#perm-det-options button").forEach(b=>b.setAttribute("aria-pressed",String(activePerm)===b.dataset.perm));
  }
  document.querySelectorAll("#perm-det-options button").forEach(b=>b.addEventListener("click",()=>{activePerm=+b.dataset.perm;leibniz()}));
  leibniz();
  const ops={
    original:[[[2,1],[3,4]],"Исходная матрица: det A = 2·4 − 1·3 = 5."],
    swap:[[[3,4],[2,1]],"Поменяли строки местами: det A′ = 3·1 − 4·2 = −5. Знак поменялся."],
    scale:[[[4,2],[3,4]],"Удвоили первую строку: det A′ = 4·4 − 2·3 = 10. Определитель удвоился."],
    add:[[[2,1],[9,7]],"Ко второй строке прибавили 3 первые: det A′ = 2·7 − 1·9 = 5. Определитель не изменился."]
  };
  function rowop(key){
    $("rowop-matrix").innerHTML=matrix(ops[key][0]);
    $("rowop-result").textContent=ops[key][1];
    document.querySelectorAll("#rowops-options button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.rowop===key));
  }
  document.querySelectorAll("#rowops-options button").forEach(b=>b.addEventListener("click",()=>rowop(b.dataset.rowop)));
  rowop("original");
  function recurrence(){
    const v=finiteValues(["rec-a","rec-b","rec-c","rec-n"],"rec-error",["rec-n"]);
    if(v===null)return;
    const [a,b,c,k]=v;
    const D=[1,a],steps=["D₀ = 1 (по соглашению)","D₁ = "+a];
    for(let i=2;i<=k;i++){
      D.push(a*D[i-1]-b*c*D[i-2]);
      steps.push("D"+i+" = "+a+"·("+D[i-1]+") − ("+b+"·"+c+")·("+D[i-2]+") = "+D[i]);
    }
    $("rec-result").innerHTML="<small>Рекурсия</small>"+steps.map(x=>"<div>"+safe(x)+"</div>").join("")+
      "<p><strong>Ответ D"+k+" = "+D[k]+"</strong>. Это определитель трёхдиагональной матрицы порядка "+k+".</p>";
  }
  ["rec-a","rec-b","rec-c","rec-n"].forEach(id=>$(id).addEventListener("input",recurrence));
  recurrence();
})();
