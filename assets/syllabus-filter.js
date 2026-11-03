"use strict";
(() => {
 const field=document.getElementById("catalog-query");
 const count=document.getElementById("catalog-count");
 if(!field||!count)return;
 const items=[...document.querySelectorAll(".catalog-item")];
 const groups=[...document.querySelectorAll("main.book section[id]")];
 const matchText=s=>s.toLocaleLowerCase("ru-RU").replace(/ё/g,"е");
 const total=items.length;
 function update(){
   const query=matchText(field.value.trim()).replace(/\s+/g," ");
   let shown=0;
   for(const item of items){
     const content=matchText(item.textContent||"");
     const matches=query===""||query.split(" ").every(word=>content.includes(word));
     item.hidden=!matches;
     item.setAttribute("aria-hidden",String(!matches));
     if(matches)shown++;
   }
   for(const section of groups){
     const existing=[...section.querySelectorAll(".catalog-item")];
     section.hidden=existing.length>0&&existing.every(e=>e.hidden);
   }
   count.textContent=query?"Найдено "+shown+" из "+total+" пунктов. Очисти поле, чтобы вернуть полный список.":"Показаны все "+total+" пункта официальной программы.";
 }
 field.addEventListener("input",update);
 field.addEventListener("keydown",ev=>{
   if(ev.key==="Escape"){field.value="";update();}
 });
 update();
})();