"use strict";
(() => {
 const $=x=>document.getElementById(x),σ=[2,1,3],τ=[1,3,2];
 const A=[7,3,2,1,6,5,4],B=[3,1,2,7,4,5,6],C=[5,1,3,6,4,7,2];
 function mulL(p,q){return p.map(v=>q[v-1]);} // apply LEFT first
 function inv(p){const r=Array(p.length).fill(0);p.forEach((v,i)=>r[v-1]=i+1);return r;}
 function equal(a,b){return a.length===b.length&&a.every((x,i)=>x===b[i]);}
 const IA=inv(A),IB=inv(B),X=mulL(mulL(IA,C),IB),check=mulL(mulL(A,X),B);
 if(!equal(check,C)||!equal(X,[7,1,2,3,4,5,6])) throw new Error("Ошибка направления композиции в задаче 178");
 let direction="left",start=1;
 function composition(){
   const p=direction==="left"?σ:τ,q=direction==="left"?τ:σ,mid=p[start-1],end=q[mid-1];
   const prod=mulL(p,q);
   $("comp-path").textContent=start+" → "+(direction==="left"?"σ":"τ")+" → "+mid+" → "+(direction==="left"?"τ":"σ")+" → "+end+". Ответ: "+end+".";
   $("comp-all").textContent="Полная двухстрочная запись: (1 2 3) → ("+prod.join(" ")+"). Это "+(direction==="left"?"σ·τ":"τ·σ")+".";
   $("normal").setAttribute("aria-pressed",direction==="left");
   $("reverse").setAttribute("aria-pressed",direction==="right");
   document.querySelectorAll("#comp-points button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.value===String(start)));
 }
 $("normal").addEventListener("click",()=>{direction="left";composition()});
 $("reverse").addEventListener("click",()=>{direction="right";composition()});
 document.querySelectorAll("#comp-points button").forEach(b=>b.addEventListener("click",()=>{start=+b.dataset.value;composition()}));
 composition();
 const examples=[[3,1,4,2],[2,3,1],[4,3,2,1],[1,2,3,4],[2,1,3,4]];
 let invSel=0;
 $("inv-options").innerHTML=examples.map((p,i)=>'<button type="button" class="btn" data-inv="'+i+'">'+p.join(" ")+"</button>").join("");
 function inversions(p){
   const pairs=[];
   for(let i=0;i<p.length;i++)for(let j=i+1;j<p.length;j++)if(p[i]>p[j])pairs.push([p[i],p[j]]);
   return pairs;
 }
 function showInv(){
   const p=examples[invSel],pairs=inversions(p),k=pairs.length;
   $("inv-result").textContent="Список ("+p.join(", ")+"). Инверсии: "+
       (k?pairs.map(x=>x[0]+">"+x[1]).join("; "):"нет")+
       ". Количество: "+k+". Знак: "+(k%2?"−1":" +1")+" ("+(k%2?"нечётная":"чётная")+" подстановка).";
   document.querySelectorAll("#inv-options button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.inv===String(invSel)));
 }
 document.querySelectorAll("#inv-options button").forEach(b=>b.addEventListener("click",()=>{invSel=+b.dataset.inv;showInv()}));
 showInv();
 let selected=1;
 $("task178-options").innerHTML=Array.from({length:7},(_,i)=>'<button class="btn" type="button" data-value="'+(i+1)+'">i = '+(i+1)+"</button>").join("");
 function show178(){
   const i=selected,a1=IA[i-1],c1=C[a1-1],b1=IB[c1-1],check2=B[X[A[i-1]-1]-1];
   $("task178-step").textContent="X("+i+") = B⁻¹(C(A⁻¹("+i+"))) = B⁻¹(C("+a1+")) = B⁻¹("+c1+") = "+b1+".";
   $("task178-check").textContent="Проверка: (AXB)("+i+") = B(X(A("+i+"))) = "+check2+" = C("+i+"). Все 7 значений: "+(equal(check,C)?"совпадают.":"ОШИБКА!");
   $("task178-answer").innerHTML="X = (1 2 3 4 5 6 7)<br>&nbsp; &nbsp; (7 1 2 3 4 5 6) = (1 7 6 5 4 3 2)";
   document.querySelectorAll("#task178-options button").forEach(b=>b.setAttribute("aria-pressed",b.dataset.value===String(i)));
 }
 document.querySelectorAll("#task178-options button").forEach(b=>b.addEventListener("click",()=>{selected=+b.dataset.value;show178()}));
 show178();
 window.__algebraPermutationVerification={convention:"left-to-right",X:X.slice(),check:equal(check,C),mulL:mulL};
})();
