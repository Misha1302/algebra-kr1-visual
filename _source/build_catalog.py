from pathlib import Path
import re,subprocess,html
from bs4 import BeautifulSoup
root=Path(__file__).resolve().parents[1]
source=(root/'_source/Algebra_KR1_2026_ONLINE.md').read_text()
def fragment(md):
 p=subprocess.run(['pandoc','-f','markdown+tex_math_dollars+raw_html','-t','html5','--mathml','--wrap=none'],input=md,text=True,capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout
def frame(title,lead,body):
 return '''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+html.escape(title)+''' · Алгебра КР №1</title><link rel="stylesheet" href="./assets/course.css"><link rel="icon" href="./favicon.svg"></head><body>
<nav class="site-nav"><div class="site-nav-inner"><a class="logo" href="./"><b>A</b>алгебра / 01</a><div class="links"><a href="./definitions.html">Определения</a><a href="./determinants.html">Определители</a><a href="./permutations.html">Подстановки</a><a href="./syllabus.html">62 пункта</a><a href="./textbook.html">Полный учебник</a></div></div></nav>
<div class="book-hero"><div class="kicker">Официальная программа · Онлайн</div><h1>'''+html.escape(title)+'''</h1><p>'''+html.escape(lead)+'''</p></div>
<div class="book-layout"><aside class="book-sidebar"><h2>Материалы</h2><a href="./textbook.html">Все главы учебника</a><a href="./proofs.html">11 доказательств</a><a href="./problems.html">12 + 13 задач</a><a href="./syllabus.html">Сверка 62 пунктов</a><a href="./determinants.html">Интерактивные определители</a><a href="./permutations.html">Подстановки слева направо</a></aside>
<main class="book">'''+body+'''</main></div><footer class="footer">Полное изложение содержится и в <a href="./textbook.html">едином онлайн-учебнике</a>.</footer></body></html>'''
def chunk(num,next_num):
 start=re.search(r'^# '+str(num)+r'\. ',source,flags=re.M).start()
 end=re.search(r'^# '+str(next_num)+r'\. ',source,flags=re.M).start() if next_num else len(source)
 return source[start:end]
proof_html=fragment(chunk(10,11))
pdoc=frame('11 доказательств','Все 11 официальных тем с подробными доказательствами и пояснениями промежуточных переходов. Не путай иллюстрацию с доказательством общего утверждения.',proof_html)
(root/'proofs.html').write_text(pdoc)
problems_html=fragment(chunk(11,13))
# Wrap each full answer in a collapsed detail: attempt first, then open.
soup=BeautifulSoup(problems_html,'html.parser')
for heading in list(soup.find_all('h2')):
 nxt=heading.find_next_sibling()
 to_wrap=[]
 while nxt is not None and nxt.name!='h2' and nxt.name!='h1':
  keep=nxt.find_next_sibling();to_wrap.append(nxt);nxt=keep
 if not to_wrap:continue
 detail=soup.new_tag('details');detail['class']='solution'
 summary=soup.new_tag('summary');summary.string='Открыть решение и пояснения'
 detail.append(summary)
 for el in to_wrap:detail.append(el.extract())
 heading.insert_after(detail)
 # Add prompt that user should attempt to solve before opening.
 note=soup.new_tag('p');note['class']='tipline';note.string='Сначала попробуй решить самостоятельно, затем раскрой подробный разбор.'
 heading.insert_after(note)
problem_doc=frame('25 задач с решениями','12 основных типов и 13 дополнительных из официального списка. Решения скрыты до нажатия: сначала попробуй самостоятельно. Порядок подстановок слева направо, как принято на курсе.',str(soup))
problem_doc=problem_doc.replace('</head>','<style>.book details.solution{border:1px solid #d8dcd8;border-radius:8px;padding:15px 19px;margin:12px 0 25px;background:#fafbf7}.book details.solution summary{cursor:pointer;color:#2146a1;font-weight:800}.book details.solution[open] summary{margin-bottom:14px}.book details.solution p:first-of-type{margin-top:10px}</style></head>')
(root/'problems.html').write_text(problem_doc)
# Extract 62 official IDs from headings.
entries=[]
in_defs=False
for line in source.splitlines():
 if line.startswith('# 9. Все 26'):in_defs=True
 if line.startswith('# 10. Все 11'):in_defs=False
 m=re.match(r'^\*\*(D\d\d)\.\s*(.*?)\*\*',line) if in_defs else None
 if m:entries.append((m.group(1),m.group(2),'Определение'))
 m=re.match(r'^## (P\d\d|T\d\d|№\d+)\.\s*(.*)',line)
 if m:
  id=m.group(1).replace('№','N')
  group='Доказательство' if id.startswith('P') else 'Основная задача' if id.startswith('T') else 'Дополнительная задача'
  entries.append((id,m.group(2),group))
assert len(entries)==62,entries
# Link to specialized pages when possible, otherwise textbook.
def link(e):
 id,title,g=e
 return ('proofs.html#' if id[0]=='P' else 'problems.html#' if id[0] in 'TN' else 'definitions.html#')+id
grps=[('Определения', 'Определение'),('Доказательства','Доказательство'),('Основные задачи','Основная задача'),('Дополнительные задачи','Дополнительная задача')]
cards=[]
for heading,cat in grps:
 chosen=[x for x in entries if x[2]==cat]
 cards.append('<section id="'+('defs' if cat=='Определение' else 'proofs' if cat=='Доказательство' else 'main' if cat=='Основная задача' else 'extra')+'"><h2>'+heading+' — '+str(len(chosen))+'</h2><div class="catalog">')
 for id,title,_ in chosen:
  short=html.escape(title)
  cards.append('<a class="catalog-item" href="./'+link((id,title,cat))+'"><span class="catalog-id">'+id.replace('N','№')+'</span><span>'+short+'</span><span class="catalog-arrow">↗</span></a>')
 cards.append('</div></section>')
base=frame('Все 62 пункта КР №1','Проверка полноты: 26 определений + 11 доказательств + 12 основных задач + 13 дополнительных. Каждый пункт ниже ведёт на полноценный разбор в HTML. Это не только карточка с названием.', ''.join(cards))
css='''<style>
.book section{margin-bottom:55px}.book section h2{font:500 32px/1.2 Georgia,serif;border-bottom:1px solid #d8dcd2;padding-bottom:15px}.catalog{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.catalog-item{padding:14px 15px;display:grid;grid-template-columns:50px minmax(0,1fr) 15px;gap:8px;align-items:start;border-radius:7px;background:#f4f7f1;border:1px solid #dce2d9;font-size:13px;text-decoration:none;color:#334b3d;line-height:1.5}.catalog-item:hover{background:#e6eefc}.catalog-id{font-weight:850;color:#254bb1}.catalog-arrow{color:#254bb1}@media(max-width:660px){.catalog{grid-template-columns:1fr}.catalog-item{grid-template-columns:43px minmax(0,1fr) 15px}.book section h2{font-size:28px}}
</style>'''
base=base.replace('</head>',css+'</head>')
(root/'syllabus.html').write_text(base)
for path,ids in [('proofs.html',['P%02d'%i for i in range(1,12)]),('problems.html',['T%02d'%i for i in range(1,13)]+['N'+str(n) for n in [184,230,231,283,299,302,348,365,853,177,178,586,829]])]:
 doc=BeautifulSoup((root/path).read_text(),'html.parser')
 missing=[i for i in ids if not doc.find(id=i)]
 assert not missing,(path,missing)
print('PAGES: proofs',len(pdoc),'problems',len(problem_doc),'syllabus',len(base),'items',len(entries))
