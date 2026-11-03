from pathlib import Path
import re,subprocess,html
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]
source=(root/'_source/Algebra_KR1_2026_SITE_CONVENTION.md').read_text()
chapter_links=[]
pieces=[]
for line in source.splitlines(keepends=True):
 m=re.match(r'^# (.*?)\s*$',line)
 if m and (m.group(1).startswith('Как пользоваться') or re.match(r'^\d+\.',m.group(1))):
  n=re.match(r'^(\d+)\.',m.group(1))
  cid='CH'+(n.group(1).zfill(2) if n else '00')
  text=m.group(1)
  chapter_links.append((cid,text))
  pieces.append('<a id="'+cid+'"></a>\n\n')
 pieces.append(line)
source=''.join(pieces)
src=root/'_source/Algebra_KR1_2026_ONLINE.md'
src.write_text(source)
p=subprocess.run(['pandoc','-f','markdown+tex_math_dollars+raw_html','-t','html5','--mathml','--wrap=none',str(src)],capture_output=True,text=True)
if p.returncode:raise RuntimeError(p.stderr)
soup=BeautifulSoup(p.stdout,'html.parser')
for heading in soup.find_all(['h1','h2','h3','h4']):
    heading.name={'h1':'h2','h2':'h3','h3':'h4','h4':'h5'}[heading.name]
body=str(soup)
nav=''.join('<a href="#'+id+'">'+html.escape(t)+'</a>' for id,t in chapter_links)
html_doc='''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Полный онлайн-учебник по КР №1: 26 определений, 11 доказательств, 12 основных и 13 дополнительных задач."><title>Полный учебник — Алгебра КР №1</title><link rel="stylesheet" href="./assets/course.css"><link rel="icon" href="./favicon.svg"></head><body>
<nav class="site-nav"><div class="site-nav-inner"><a class="logo" href="./"><b>A</b>алгебра / 01</a><div class="links"><a href="./definitions.html">Определения</a><a href="./determinants.html">Определители</a><a href="./permutations.html">Подстановки</a><a href="./practice.html">Практика</a><a href="./exam.html">Диагностика КР</a><a href="./syllabus.html">Все 62 пункта</a></div></div></nav>
<div class="book-hero"><div class="kicker">Полный онлайн-учебник · КР №1 · 2026</div><h1>Все темы, доказательства и задачи в одном месте</h1>
<p>Текст включает полный учебный материал: объяснения, 26 определений, 11 подробных доказательств, 12 основных и 13 дополнительных задач с решениями. Используй боковое оглавление или <a href="./syllabus.html">карту официальных вопросов</a>.</p>
<div class="notice"><strong>Важно — подстановки слева направо:</strong> в этом онлайн-издании произведение σ·τ означает «сначала σ, затем τ»: (στ)(i)=τ(σ(i)). В прежней версии загружаемого визуального PDF был другой порядок; для произведений подстановок опирайся на эту исправленную онлайн-версию. В задаче №178 ответ пересчитан.</div>
</div>
<div class="book-layout"><aside class="book-sidebar" aria-label="Содержание учебника"><h2>Разделы учебника</h2>'''+nav+'''</aside>
<main class="book" id="full-textbook">'''+body+'''</main></div><footer class="footer">Алгебра КР №1 · Полное онлайн-издание · <a href="./syllabus.html">Проверить покрытие 62 пунктов</a></footer></body></html>'''
(root/'textbook.html').write_text(html_doc)
doc=BeautifulSoup(html_doc,'html.parser')
expected=['D%02d'%n for n in range(1,27)]+['P%02d'%n for n in range(1,12)]+['T%02d'%n for n in range(1,13)]+['N'+str(n) for n in [184,230,231,283,299,302,348,365,853,177,178,586,829]]
missing=[i for i in expected if doc.find(id=i) is None]
assert not missing,missing
assert len(doc.select('main.book > h2'))>=15 and len(doc.select('h1'))==1
assert len(doc.find_all('math'))>50, len(doc.find_all('math'))
assert 'B(X(A(1)))' in source
assert 'A(X(B(1)))' not in source
print('HTML generated:',(root/'textbook.html').stat().st_size,'bytes; chapters',len(chapter_links),'mathML',len(doc.find_all('math')),'syllabus',len(expected))
