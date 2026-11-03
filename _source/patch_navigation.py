from pathlib import Path
root=Path('/home/micodiy/razakov/sites/algebra-kr1-visual')
p=root/'index.html';s=p.read_text()
s=s.replace('<a href="#program">Программа</a><a href="./definitions.html">Определения</a>','<a href="./syllabus.html">62 пункта</a><a href="./definitions.html">Определения</a>')
s=s.replace('<a class="nav-cta" href="./lab.html">Открыть лабораторию ↗</a>','<a class="nav-cta" href="./textbook.html">Полный учебник ↗</a>')
s=s.replace('<a class="button secondary" href="./lab.html">Перейти к лаборатории','<a class="button secondary" href="./textbook.html">Полный учебник')
s=s.replace('<div class="facts" aria-label="Содержание курса">','''<div class="facts" aria-label="Содержание курса">
        <div class="fact"><span class="number">62</span><span class="description">официальных пункта<br>с полными разборами</span></div>''')
# Facts previously 3 now 4 -> style.
s=s.replace('grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line)','grid-template-columns:repeat(4,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line)')
s=s.replace('.fact{display:block;padding:22px 16px}', '.fact{display:block;padding:17px 10px}')
s=s.replace('.fact .number{font-size:32px}', '.fact .number{font-size:27px}')
s=s.replace('.fact .description{font-size:11px}', '.fact .description{font-size:10px}')
s=s.replace('@media(max-width:550px){.top nav .nav-cta{display:none}.top nav a[href="./definitions.html"]{display:inline}', '@media(max-width:550px){.top nav .nav-cta{display:none}.top nav a[href="./definitions.html"]{display:inline}')
anchor='<section class="section">'
assert anchor in s
new='''<section class="section" id="all-topics">
      <div class="wrap">
        <div class="section-tag">Полная программа · а не только умножение матриц</div>
        <div class="section-head"><h2>Выбери тему,<br>которую не понимаешь.</h2><p>Здесь есть самостоятельные наглядные уроки, все доказательства и все официальные типы задач. Можно идти прямо к нужной теме.</p></div>
        <div class="curriculum">
          <a class="topic" href="./determinants.html"><span class="id">ОТ ОСНОВ К 3×3 И n×n</span><h3>Определители, свойства, рекурсии ↗</h3></a>
          <a class="topic" href="./permutations.html"><span class="id">ПО КОНВЕНЦИИ КУРСА</span><h3>Подстановки слева направо ↗</h3></a>
          <a class="topic" href="./lab.html"><span class="id">8 ТРЕНАЖЁРОВ</span><h3>Матрицы, Гаусс, ранг, LU ↗</h3></a>
          <a class="topic" href="./textbook.html"><span class="id">ПОЛНОЕ ИЗЛОЖЕНИЕ</span><h3>Учебник с формулами ↗</h3></a>
          <a class="topic" href="./definitions.html"><span class="id">D01–D26</span><h3>26 определений с примерами ↗</h3></a>
          <a class="topic" href="./proofs.html"><span class="id">P01–P11</span><h3>11 доказательств ↗</h3></a>
          <a class="topic" href="./problems.html"><span class="id">T01–T12 + №</span><h3>25 задач и скрытые решения ↗</h3></a>
          <a class="topic" href="./syllabus.html"><span class="id">АУДИТ ПОЛНОТЫ</span><h3>Чек-лист 62 пунктов ↗</h3></a>
        </div>
      </div>
    </section>
    '''
s=s.replace(anchor,new+anchor,1)
s=s.replace('.topic .id{font-size:12px;color:var(--blue);font-weight:800}', '.topic .id{font-size:12px;color:var(--blue);font-weight:800}.topic{text-decoration:none;transition:border-color .2s,transform .2s}.topic:hover{border-color:#7290d2;transform:translateY(-2px)}')
s=s.replace('<a class="starter-link" href="./definitions.html">Открыть понятный словарь всех 26 определений ↗</a>', '<a class="starter-link" href="./definitions.html">Открыть понятный словарь всех 26 определений ↗</a>')
s=s.replace('<a href="./assets/Algebra_KR1_2026_VISUAL.pdf" target="_blank" rel="noopener">Открыть пособие · 53 стр. ↗</a>', '<a href="./textbook.html">Открыть полную исправленную онлайн-версию ↗</a>')
s=s.replace('Основной материал · PDF', 'Главный материал · полный онлайн-учебник')
s=s.replace('<a href="./assets/KR1_Answer_Key.pdf" target="_blank" rel="noopener">Ответы к мини-КР ↗</a>', '<a href="./assets/KR1_Answer_Key.pdf" target="_blank" rel="noopener">Ответы к мини-КР ↗</a><a href="./assets/Algebra_KR1_2026_VISUAL.pdf" target="_blank" rel="noopener">Прежний наглядный PDF (порядок подстановок в нём отличается) ↗</a>')
p.write_text(s)
d=root/'definitions.html';a=d.read_text()
a=a.replace('<a href="./assets/Algebra_KR1_2026_VISUAL.pdf" target="_blank" rel="noopener">Полный учебник ↗</a>','<a href="./textbook.html">Полный учебник ↗</a>')
a=a.replace('<a href="./lab.html#matrix">Попробовать умножение на этой матрице ↗</a>', '<a href="./lab.html#matrix">Попробовать умножение на этой матрице ↗</a>')
a=a.replace('<p>Это не список слов для заучивания.', '<p><a href="./determinants.html">Определители с нуля ↗</a> · <a href="./permutations.html">Подстановки слева направо ↗</a></p><p>Это не список слов для заучивания.')
d.write_text(a)
l=root/'lab.html';t=l.read_text()
t=t.replace('<a href="./assets/Algebra_KR1_2026_VISUAL.pdf">Учебник PDF</a>','<a href="./textbook.html">Полный учебник</a> &nbsp;·&nbsp; <a href="./determinants.html">Определители</a> &nbsp;·&nbsp; <a href="./permutations.html">Подстановки</a>')
l.write_text(t)
# Update dictionary links to relevant self-contained lessons.
q=root/'glossary.js';j=q.read_text()
j=j.replace('const link=pdf?"./assets/Algebra_KR1_2026_VISUAL.pdf":"./lab.html#"+encodeURIComponent(tab);',
'''const topics={D05:"./permutations.html#basics",D06:"./permutations.html#sign",D07:"./determinants.html#leibniz",D08:"./determinants.html#laplace",D09:"./determinants.html#laplace",D10:"./determinants.html#properties",D11:"./textbook.html#D11",D15:"./textbook.html#D15"};
    const link=topics[id]|| (pdf?"./textbook.html#"+id:"./lab.html#"+encodeURIComponent(tab));''')
j=j.replace('const label=pdf?"Читать подробный разбор в PDF ↗":"Увидеть пример в лаборатории ↗";','const label=pdf?"Читать подробный разбор онлайн ↗":"Увидеть пример в уроке / лаборатории ↗";')
q.write_text(j)
# Ensure all external-facing HTML links point at dedicated sections or full HTML, not stale PDF.
smap=root/'sitemap.xml';sm=smap.read_text()
new_urls=['textbook.html','determinants.html','permutations.html','syllabus.html','proofs.html','problems.html']
for filename in new_urls:
 if '/'+filename+'</loc>' not in sm:
  sm=sm.replace('</urlset>','<url><loc>https://misha1302.github.io/algebra-kr1-visual/'+filename+'</loc></url>\n</urlset>')
smap.write_text(sm)
print('Nav and links patched, sitemap urls:',len(new_urls))
