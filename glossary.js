"use strict";
(function(){
  const data=typeof DICTIONARY!=="undefined" ? DICTIONARY : [];
  const root=document.getElementById("definitions");
  const filters=document.getElementById("filters");
  const result=document.getElementById("result");
  const search=document.getElementById("search");
  if(!root||!filters||!search) return;
  const categoryNames=["Все"].concat(Array.from(new Set(data.map(x=>x[2]))));
  let category="Все",query="";
  const escapeText=x=>String(x).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
  const inPdf=new Set(["D05","D06","D07","D09","D10","D11","D15"]);
  function card(d){
    const [id,term,group,plain,formal,example,tab]=d;
    const pdf=inPdf.has(id);
    const topics={D05:"./permutations.html#basics",D06:"./permutations.html#sign",D07:"./determinants.html#leibniz",D08:"./determinants.html#laplace",D09:"./determinants.html#laplace",D10:"./determinants.html#properties",D11:"./textbook.html#D11",D15:"./textbook.html#D15"};
    const link=topics[id]|| (pdf?"./textbook.html#"+id:"./lab.html#"+encodeURIComponent(tab));
    const label=pdf?"Читать подробный разбор онлайн ↗":"Увидеть пример в уроке / лаборатории ↗";
    return '<article class="def" id="'+escapeText(id)+'">'+
      '<div class="top"><span class="id">'+escapeText(id)+'</span><span class="group">'+escapeText(group)+'</span></div>'+
      '<h3>'+escapeText(term)+'</h3>'+
      '<p><b>Простыми словами</b>'+escapeText(plain)+'</p>'+
      '<p class="formal"><b>Определение или теорема</b>'+escapeText(formal)+'</p>'+
      '<p class="example"><b>На конкретном примере</b>'+escapeText(example)+'</p>'+
      '<a href="'+link+'"'+(pdf?' target="_blank" rel="noopener"':'')+'>'+label+'</a>'+
    '</article>';
  }
  function renderFilters(){
    filters.innerHTML=categoryNames.map(n=>
      '<button type="button" data-filter="'+escapeText(n)+'" class="'+(category===n?'active':'')+'" aria-pressed="'+(category===n?'true':'false')+'">'+escapeText(n)+'</button>'
    ).join("");
    filters.querySelectorAll("button").forEach(b=>b.addEventListener("click",()=>{
      category=b.getAttribute("data-filter");draw();
    }));
  }
  function draw(){
    renderFilters();
    const q=query.toLocaleLowerCase("ru").trim();
    const shown=data.filter(d=>(category==="Все"||d[2]===category)&&(!q||d.slice(0,6).join(" ").toLocaleLowerCase("ru").includes(q)));
    root.innerHTML=shown.length?shown.map(card).join(""):'<p class="empty">Ничего не нашлось. Попробуй другое слово или убери фильтр.</p>';
    result.textContent="Показано "+shown.length+" из "+data.length+" понятий";
  }
  search.addEventListener("input",()=>{query=search.value;draw();});
  draw();
  if(/^#D\d\d$/.test(location.hash)){
    const el=document.getElementById(location.hash.slice(1));
    if(el) requestAnimationFrame(()=>el.scrollIntoView({block:"start"}));
  }
})();