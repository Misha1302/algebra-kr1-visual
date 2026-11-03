"use strict";
(function(){
const $=id=>document.getElementById(id);
const A=[[1,2,3],[4,5,6]],B=[[7,8],[9,10],[11,12]],A3=[[1,2,3],[0,4,5],[1,0,6]];
const subscript=x=>String(x).split("").map(d=>"₀₁₂₃₄₅₆₇₈₉"[Number(d)]).join("");
const numberText=x=>String(x).replace(/-/g,"−");
function render(id,rows,style,click){
 const container=$(id);if(!container)return;
 container.innerHTML=rows.map((row,i)=>row.map((value,j)=>{
  const cls="v "+(style?style(i,j):"");
  const aria=' aria-label="Строка '+(i+1)+', столбец '+(j+1)+', значение '+value+'"';
  const content=String(value);
  return click?'<button type="button" class="'+cls+'" data-i="'+i+'" data-j="'+j+'"'+aria+'>'+content+'</button>':'<span class="'+cls+'">'+content+'</span>';
 }).join("")).join("");
 if(click)container.querySelectorAll("button").forEach(button=>button.addEventListener("click",()=>click(+button.dataset.i,+button.dataset.j)));
}
function matBlock(rows,label){
 return '<div class="mat-wrap"><div class="mat-label">'+label+'</div><div class="mat" style="--cols:'+rows[0].length+'">'+
 rows.map(row=>row.map(value=>'<span class="v">'+numberText(value)+'</span>').join("")).join("")+'</div></div>';
}
// 1: See how a matrix coordinate works.
function address(i,j){
 document.querySelectorAll("#base-matrix button").forEach(b=>{
  const hit=+b.dataset.i===i&&+b.dataset.j===j;
  b.classList.toggle("sel-h",hit);b.setAttribute("aria-pressed",String(hit));
 });
 $("base-explain").textContent="Число "+A[i][j]+": строка "+(i+1)+", столбец "+(j+1)+". Адрес a"+subscript(i+1)+subscript(j+1)+" = "+A[i][j]+".";
}
document.querySelectorAll("#base-matrix button").forEach(b=>b.addEventListener("click",()=>address(+b.dataset.i,+b.dataset.j)));
address(1,2);
// 2: Row by column.
const P=A.map(row=>B[0].map((_,j)=>row.reduce((s,v,k)=>s+v*B[k][j],0)));
let selectedRow=0,selectedCol=0,mulPhase=0;
function multiplication(){
 render("mul-A",A,(i,j)=>i===selectedRow?"row-h":"");
 render("mul-B",B,(i,j)=>j===selectedCol?"col-h":"");
 render("mul-C",P,(i,j)=>i===selectedRow&&j===selectedCol?"sel-h":"",(i,j)=>{
  selectedRow=i;selectedCol=j;mulPhase=0;multiplication();
 });
 const row=A[selectedRow],col=B.map(r=>r[selectedCol]),products=row.map((v,k)=>v*col[k]);
 const phrases=[
  "Выбрали строку "+(selectedRow+1)+" из A и столбец "+(selectedCol+1)+" из B.",
  "Сопоставили первую пару: "+row[0]+" и "+col[0]+".",
  "Добавили вторую пару: "+row[1]+" и "+col[1]+".",
  "Добавили последнюю пару. Все произведения складываются."
 ];
 const lines=[
  "("+row.join(", ")+") · ("+col.join(", ")+")",
  row[0]+"·"+col[0]+" = "+products[0],
  row[0]+"·"+col[0]+" + "+row[1]+"·"+col[1]+" = "+products[0]+" + "+products[1]+" = "+(products[0]+products[1]),
  row[0]+"·"+col[0]+" + "+row[1]+"·"+col[1]+" + "+row[2]+"·"+col[2]+" = "+products.join(" + ")+" = "+P[selectedRow][selectedCol]
 ];
 $("mul-step-text").textContent=phrases[mulPhase];$("mul-equation").textContent=lines[mulPhase];
 $("mul-hint").textContent="Это элемент c"+subscript(selectedRow+1)+subscript(selectedCol+1)+". Длина обоих списков равна 3.";
 $("mul-next").disabled=mulPhase>=3;
 $("mul-next").textContent=mulPhase<3?"Следующий промежуточный шаг →":"Все пары посчитаны";
}
$("mul-next").addEventListener("click",()=>{mulPhase=Math.min(3,mulPhase+1);multiplication()});
$("mul-restart").addEventListener("click",()=>{mulPhase=0;multiplication()});
multiplication();
// 3: Compatible dimensions.
function sizes(ok){
 $("size-ok").setAttribute("aria-pressed",String(ok));$("size-bad").setAttribute("aria-pressed",String(!ok));
 $("size-visual").innerHTML=ok?
 '<strong>Совместимо:</strong> строка A (1,2,3) накладывается на столбец B (7,9,11). <span class="mathline">1↔7, 2↔9, 3↔11</span>Всем хватает пары; размер ответа 2×2.':
 '<strong>Нельзя:</strong> строка A (1,2,3), столбец B (7,9). <span class="mathline">1↔7, 2↔9, 3↔?</span>Третьей пары нет. Произведение 2×3 на 2×2 не определено.';
}
$("size-ok").addEventListener("click",()=>sizes(true));$("size-bad").addEventListener("click",()=>sizes(false));sizes(true);
// 4: Transpose.
const AT=A[0].map((_,j)=>A.map(row=>row[j]));
function transpose(i,j){
 render("tr-A",A,(r,c)=>r===i&&c===j?"row-h":"",(r,c)=>transpose(r,c));
 render("tr-T",AT,(r,c)=>r===j&&c===i?"sel-h":"");
 $("tr-caption").textContent="Число "+A[i][j]+" переместилось из ("+(i+1)+","+(j+1)+") в ("+(j+1)+","+(i+1)+"). Значение не поменялось.";
}
transpose(1,2);
// 5: Gauss with actual row operations.
const G=[
 {m:[[1,1,3],[2,-1,0]],label:"Исходная матрица",operation:"Сначала выбираем ведущий коэффициент 1 в первой строке.",equation:"x+y=3; 2x−y=0",reason:"Первую строку используем, чтобы исключить x из второго уравнения."},
 {m:[[1,1,3],[0,-3,-6]],label:"После исключения x",operation:"R₂ ← R₂ − 2R₁. Вычитаем удвоенную первую строку из второй.",equation:"[2,−1 | 0] − 2·[1,1 | 3] = [0,−3 | −6]",reason:"Коэффициент при x во второй строке стал нулём. Это ступенчатый вид."},
 {m:[[1,1,3],[0,1,2]],label:"После нормировки",operation:"R₂ ← R₂ /(−3). Делим всю вторую строку на ненулевое число.",equation:"[0,−3 | −6] /(−3) = [0,1 | 2]",reason:"Вторая строка означает y = 2."},
 {m:[[1,0,1],[0,1,2]],label:"Приведённая ступенчатая форма",operation:"R₁ ← R₁ − R₂. Убираем y из первой строки.",equation:"[1,1 | 3] − [0,1 | 2] = [1,0 | 1]",reason:"Ответ x = 1, y = 2. Проверь обе исходные строки."}
];
let gaussStep=0;
function gaussian(){
 const g=G[gaussStep];
 render("gauss-matrix",g.m,(i,j)=>j===2?"focus":gaussStep>0&&i===1?"sel-h":"");
 $("gauss-label").textContent=g.label;$("gauss-count").textContent=String(gaussStep);
 $("gauss-operation").textContent=g.operation;$("gauss-equation").textContent=g.equation;
 $("gauss-why").textContent=g.reason;
 $("gauss-prev").disabled=gaussStep===0;$("gauss-next").disabled=gaussStep===G.length-1;
}
$("gauss-next").addEventListener("click",()=>{gaussStep=Math.min(G.length-1,gaussStep+1);gaussian()});
$("gauss-prev").addEventListener("click",()=>{gaussStep=Math.max(0,gaussStep-1);gaussian()});
$("gauss-reset").addEventListener("click",()=>{gaussStep=0;gaussian()});gaussian();
// 6: Permutation mapping.
const sigma=[2,3,1];
function perm(i){
 $("permutation-caption").textContent="σ("+i+")="+sigma[i-1]+". Цикл: 1→2→3→1. При произведении στ сначала действует σ, затем τ.";
 $("permutation-points").querySelectorAll("button").forEach(b=>b.setAttribute("aria-pressed",String(+b.dataset.p===i)));
}
$("permutation-points").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>perm(+b.dataset.p)));perm(1);
// 7: Cofactor, delete row and column.
function det2(m){return m[0][0]*m[1][1]-m[0][1]*m[1][0]}
function cofactor(i,j){
 const sub=A3.filter((_,r)=>r!==i).map(row=>row.filter((_,c)=>c!==j));
 const minor=det2(sub),sgn=(i+j)%2?-1:1;
 render("cofactor-A",A3,(r,c)=>r===i&&c===j?"sel-h":r===i||c===j?"gone":"",(r,c)=>cofactor(r,c));
 render("cofactor-small",sub);
 $("cofactor-caption").textContent="Выбрано a"+subscript(i+1)+subscript(j+1)+"="+A3[i][j]+". Вычеркнули строку "+(i+1)+", столбец "+(j+1)+". M="+sub[0][0]+"·"+sub[1][1]+"−"+sub[0][1]+"·"+sub[1][0]+"="+numberText(minor)+". Знак "+(sgn>0?"+":"−")+"; дополнение C="+numberText(sgn*minor)+".";
}
cofactor(0,1);
// 8: Inverse matrix constructed by five explicit stages.
const stages=[
 {m:[[2,1],[3,4]],name:"Исходная A",text:"A = [[2,1],[3,4]]. det A = 2·4 − 1·3 = 5, значит обратная матрица существует."},
 {m:[[4,-3],[-1,2]],name:"Матрица дополнений C",text:"C₁₁ = 4, C₁₂ = −3, C₂₁ = −1, C₂₂ = 2. Шахматка знаков + − / − +."},
 {m:[[4,-1],[-3,2]],name:"Союзная adj(A) = Cᵀ",text:"Транспонируем матрицу дополнений: меняем местами C₁₂ и C₂₁. Это adj(A), пока ещё не обратная!"},
 {m:[["4/5","−1/5"],["−3/5","2/5"]],name:"Обратная A⁻¹",text:"Все элементы adj(A) делим на один определитель 5. Получаем обратную."},
 {m:[[1,0],[0,1]],name:"Проверка: A·A⁻¹ = I",text:"Умножаем A на adj(A): [[5,0],[0,5]] = 5I. После деления на 5 получаем единичную матрицу."}
];
let invStage=0;
function inverse(){
 const v=stages[invStage];
 $("inverse-stage").innerHTML=matBlock(v.m,v.name);
 $("inverse-caption").textContent="Этап "+(invStage+1)+" из 5. "+v.text;
 $("inverse-prev").disabled=invStage===0;$("inverse-next").disabled=invStage===4;
}
$("inverse-prev").addEventListener("click",()=>{invStage=Math.max(0,invStage-1);inverse()});
$("inverse-next").addEventListener("click",()=>{invStage=Math.min(4,invStage+1);inverse()});
$("inverse-reset").addEventListener("click",()=>{invStage=0;inverse()});inverse();
// 9: Parameter alters the rank exactly at zero.
function rank(){
 const t=Number($("rank-t").value),m=[[1,2,3],[2,4+t,6+t]];
 render("rank-matrix",m,(i,j)=>j<2?"row-h":"sel-h");
 render("rank-sub",[[1,2],[2,4+t]]);
 $("rank-t-label").textContent=numberText(t);
 $("rank-det").textContent="det [[1,2],[2,"+(4+t)+"]] = 1·("+(4+t)+") − 2·2 = "+t;
 $("rank-answer").textContent="rank A = "+(t===0?1:2);
 $("rank-caption").textContent=t===0?"При t=0 вторая строка удваивает первую. Ненулевая строка остаётся, поэтому ранг равен 1, а не 0.":
  "При t="+t+" квадратный минор по первым двум столбцам отличен от нуля. Есть две независимые строки, rank A = 2. Третий столбец = сумма первых двух.";
}
$("rank-t").addEventListener("input",rank);
$("rank-zero").addEventListener("click",()=>{$("rank-t").value=0;rank()});rank();
// 10: Kronecker–Capelli, three different systems.
const systems={
 many:{m:[[1,1,2],[2,2,4]],desc:"Второе уравнение — в точности удвоенное первое: они задают одну прямую.",op:"R₂ ← R₂ − 2R₁",out:"[0, 0 | 0]",verdict:"rank A = rank[A|b] = 1, неизвестных 2. Решений бесконечно много: x=2−t, y=t.",bad:false},
 none:{m:[[1,1,2],[2,2,5]],desc:"Первое требует 2x+2y=4, второе — 2x+2y=5. Противоречие.",op:"R₂ ← R₂ − 2R₁",out:"[0, 0 | 1]",verdict:"rank A = 1, rank[A|b] = 2. Ранги не совпали, получаем 0=1: решений нет.",bad:true},
 one:{m:[[1,1,2],[1,-1,0]],desc:"Две независимые прямые пересекаются в одной точке (1,1).",op:"R₂ ← R₂ − R₁",out:"[0, −2 | −2]",verdict:"rank A = rank[A|b] = 2 = числу неизвестных. Единственное решение x=y=1.",bad:false}
};
function system(k){
 const v=systems[k];
 render("system-matrix",v.m,(i,j)=>j===2?"focus":i===1?"row-h":"");
 $("system-description").textContent=v.desc;$("system-operation").textContent=v.op;
 $("system-result").textContent=v.out;$("system-verdict").textContent=v.verdict;
 $("system-verdict").classList.toggle("bad",v.bad);
 $("system-controls").querySelectorAll("button").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.system===k)));
}
$("system-controls").querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>system(b.dataset.system)));system("many");
// 11: Questions with explanations, not just correct/incorrect labels.
const explain={
 matrix:{
  yes:"Да: 4 строки первой матрицы и 2 столбца второй. Внутренние размеры совпадают — по 3.",
  bad:"У результата остаются внешние размеры. Проверь: внутренние 3 и 3 равны, а снаружи 4 и 2."
 },
 gauss:{
  yes:"Да: правую часть преобразуем точно так же, как коэффициенты. 0−2·3 = −6.",
  bad:"Не пропускай правую часть. Когда вычитаешь две первые строки, число справа тоже изменяется."
 },
 det:{
  yes:"Да! Минор M₁₂ = 0·6−5·1 = −5. На позиции (1,2) знак отрицателен; C₁₂ = −(−5)=+5.",
  bad:"Сначала вычисли M₁₂ после удаления строки 1 и столбца 2, затем добавь шахматный знак −."
 },
 inverse:{
  yes:"Да: для y заменили второй столбец A, получили det A₂=9, а det A=5. Результат y=9/5.",
  bad:"Знаменатель в Крамере один — det A=5. При нахождении y меняется второй столбец, его новый определитель равен 9."
 },
 rank:{
  yes:"Да: вторая строка равна удвоенной первой, но первая ненулевая. Осталось одно независимое направление.",
  bad:"У ранг ноль только нулевая матрица. Здесь есть ненулевая строка, но вторая полностью от неё зависит."
 },
 systems:{
  yes:"Да: rank A = rank[A|b], значит система совместна. Но общий ранг 2 меньше числа неизвестных 3 — есть свободный параметр.",
  bad:"Сравни сначала два ранга: они равны, поэтому решения существуют. Далее общий ранг меньше числа неизвестных."
 },
 advanced:{
  yes:"Да: два независимых столбца и один, получаемый их суммой, дают ранг 2.",
  bad:"Третий столбец не добавляет независимой информации. Два первых независимы, значит ранг 2."
 }
};
const storeKey="algebra-kr1-course-7-chapters-v1";
let done={};
try{done=JSON.parse(localStorage.getItem(storeKey)||"{}")||{}}catch(_){done={}}
function progress(){
 const n=Object.keys(explain).filter(k=>done[k]).length;
 $("chapter-progress").textContent=n+"/7";
}
document.querySelectorAll(".quickcheck").forEach(section=>{
 const topic=section.dataset.check,feedback=section.querySelector(".feedback");
 const buttons=section.querySelectorAll("button[data-answer]");
 buttons.forEach(button=>button.addEventListener("click",()=>{
  const correct=button.dataset.answer==="yes";
  buttons.forEach(b=>b.classList.toggle("chosen",b===button));
  feedback.hidden=false;feedback.classList.toggle("bad",!correct);
  feedback.textContent=explain[topic][correct?"yes":"bad"];
  if(correct){done[topic]=true;try{localStorage.setItem(storeKey,JSON.stringify(done))}catch(_){}progress()}
 }));
});
progress();
const nav=document.querySelectorAll(".course-nav a");
const observer=new IntersectionObserver(entries=>{
 const active=entries.filter(x=>x.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top)[0];
 if(!active)return;
 nav.forEach(link=>{
  const current=link.getAttribute("href")==="#"+active.target.id;
  if(current)link.setAttribute("aria-current","location");else link.removeAttribute("aria-current");
 });
},{rootMargin:"-5% 0px -75% 0px",threshold:0});
document.querySelectorAll("section.chapter").forEach(el=>observer.observe(el));
})();
