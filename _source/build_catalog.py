"""Generate official catalog, readable practice conditions and proof workshops.

Source of truth:
 * _source/Algebra_KR1_2026_ONLINE.md — worked solutions and full proofs
 * _source/practice_statements.md — official statements without answers
 * _source/practice_hints.json — optional, method-only hints
 * _source/proof_workshop.json — proof scaffolds/checks
"""
from pathlib import Path
import html
import json
import re
import subprocess
from bs4 import BeautifulSoup

root=Path(__file__).resolve().parents[1]
source=(root/'_source/Algebra_KR1_2026_ONLINE.md').read_text(encoding='utf8')

def fragment(md):
    p=subprocess.run(
        ['pandoc','-f','markdown+tex_math_dollars+tex_math_single_backslash+raw_html','-t','html5','--mathml','--wrap=none'],
        input=md,text=True,capture_output=True,check=False
    )
    if p.returncode:raise RuntimeError(p.stderr)
    return p.stdout

def frame(title,lead,body,extras=''):
    return '''<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>'''+html.escape(title)+''' · Алгебра КР №1</title>
<link rel="stylesheet" href="./assets/course.css">
<link rel="stylesheet" href="./assets/practice.css">
<link rel="icon" type="image/svg+xml" href="./favicon.svg">'''+extras+'''</head><body>
<nav class="site-nav"><div class="site-nav-inner"><a class="logo" href="./"><b>A</b>алгебра / 01</a>
<div class="links"><a href="./definitions.html">Учебник с нуля</a><a href="./practice.html">Самостоятельная практика</a>
<a href="./proofs.html">Доказательства</a><a href="./problems.html">Задачи</a>
<a href="./syllabus.html">Все 62 пункта</a><a href="./textbook.html">Полный учебник</a></div></div></nav>
<div class="book-hero"><div class="kicker">Программа КР №1 · интерактивное издание</div><h1>'''+html.escape(title)+'''</h1><p>'''+html.escape(lead)+'''</p></div>
<div class="book-layout"><aside class="book-sidebar" aria-label="Другие материалы">
<div class="nav-heading">Материалы</div><a href="./definitions.html">Обучение с нуля</a>
<a href="./practice.html">Практика на новых числах</a><a href="./exam.html">Диагностика КР</a>
<a href="./textbook.html">Все главы учебника</a><a href="./proofs.html">11 доказательств</a>
<a href="./problems.html">25 официальных задач</a><a href="./syllabus.html">Сверка 62 пунктов</a>
<a href="./determinants.html">Интерактивные определители</a><a href="./permutations.html">Подстановки слева направо</a>
</aside><main class="book" id="main-content">'''+body+'''</main></div>
<footer class="footer">Алгебра КР №1 · <a href="./textbook.html">Полный учебник</a> ·
<a href="./practice.html">Тренировка переноса навыков</a></footer></body></html>'''

def chunk(num,next_num):
    m=re.search(r'^# '+str(num)+r'\. ',source,flags=re.M)
    assert m,('missing source heading',num)
    start=m.start()
    end=re.search(r'^# '+str(next_num)+r'\. ',source,flags=re.M).start() if next_num else len(source)
    return source[start:end]

def read_statements():
    raw=(root/'_source/practice_statements.md').read_text(encoding='utf8')
    chunks=re.split(r'^## ((?:T\d{2})|(?:N\d{3}))\s*$',raw,flags=re.M)
    assert len(chunks)==51,len(chunks)
    return {chunks[i]:chunks[i+1].strip() for i in range(1,len(chunks),2)}

def after_heading_until_next(h):
    to_wrap=[]
    node=h.find_next_sibling()
    while node is not None and node.name not in ('h1','h2'):
        after=node.find_next_sibling()
        to_wrap.append(node)
        node=after
    return to_wrap

def soup_node(markup):
    s=BeautifulSoup(markup,'html.parser')
    assert len(s.contents)==1,repr(markup[:300])
    return s.contents[0]

def heading_levels(s):
    # The page frame owns the single H1. Keep all existing IDs and deep links.
    for h in s.find_all(re.compile(r'^h[1-5]$')):
        if h.name=='h1':h.name='h2'
        elif h.name=='h2':h.name='h3'
        elif h.name=='h3':h.name='h4'
    return s

statements=read_statements()
assert len(statements)==25
hints=json.loads((root/'_source/practice_hints.json').read_text(encoding='utf8'))
variants=json.loads((root/'_source/practice_variants.json').read_text(encoding='utf8'))
assert set(variants)==set(statements),(set(variants)^set(statements))

problem_soup=BeautifulSoup(fragment(chunk(11,13)),'html.parser')
seen=set()
for h in list(problem_soup.find_all('h2')):
    title=h.get_text(' ',strip=True)
    match=re.match(r'^(T\d{2}|№\d{3})\.',title)
    if not match:continue
    ident=match.group(1).replace('№','N')
    assert ident in statements,ident
    assert ident not in seen,ident
    seen.add(ident)
    original=after_heading_until_next(h)
    detail=problem_soup.new_tag('details')
    detail['class']='solution'
    detail['data-problem']=ident
    summary=problem_soup.new_tag('summary')
    summary.string='Показать подробное решение и проверку'
    detail.append(summary)
    for node in original:detail.append(node.extract())
    h.insert_after(detail)
    # The complete independent condition is outside both hint and solution disclosures.
    shown=soup_node(
        '<div class="problem-statement" role="group" aria-label="Условие задачи '+ident+'">'
        '<div class="micro">УСЛОВИЕ · '+ident+' · доступно до подсказок</div>'
        +fragment(statements[ident])+'</div>'
    )
    detail.insert_before(shown)
    method=hints.get(ident,{})
    steps=method.get('hints',['Определи тип задачи и выпиши известные условия.','Проверь необходимые условия применимости метода.'])
    hint_html=''.join(
        '<details class="method-hint"><summary>Подсказка '+str(i+1)+' без ответа</summary><p>'+html.escape(step)+'</p></details>'
        for i,step in enumerate(steps[:2])
    )
    controls=soup_node(
        '<div class="attempt-workspace" data-problem="'+ident+'">'
        '<label for="attempt-'+ident+'">Мой ход решения (черновик, не проверяется автоматически)</label>'
        '<textarea id="attempt-'+ident+'" rows="4" spellcheck="false" placeholder="Запиши промежуточные шаги, преобразования, обоснования и ответ."></textarea>'
        '<div class="attempt-actions"><button type="button" data-save-attempt>Сохранить черновик на этом устройстве</button>'
        '<span class="save-message" aria-live="polite"></span></div>'
        '<p class="attempt-disclaimer">Для проверки открой эталон только после собственной попытки. Совпадение ответа не гарантирует корректность метода.</p>'
        '</div>'
    )
    shown.insert_after(controls)
    hint_group=soup_node('<div class="method-hints">'+hint_html+'</div>')
    controls.insert_after(hint_group)
    variation=variants[ident]
    variant_html=(
        '<details class="practice-variant" data-variant="'+ident+'">'
        '<summary>Незнакомые условия: попробовать новый вариант '+ident+'</summary>'
        '<div class="problem-statement"><div class="micro">НОВЫЕ ДАННЫЕ · тот же метод · '+ident+'</div>'
        +fragment(variation['statement'])+'</div>'
        '<div class="attempt-workspace" data-problem="'+ident+'-new">'
        '<label for="variant-attempt-'+ident+'">Мой метод и вычисления нового варианта</label>'
        '<textarea id="variant-attempt-'+ident+'" rows="4" placeholder="Сначала реши без эталона…"></textarea>'
        '<div class="attempt-actions"><button type="button" data-save-attempt>Сохранить черновик на устройстве</button>'
        '<span class="save-message" aria-live="polite"></span></div></div>'
        '<details class="variant-solution"><summary>Проверить новый вариант по эталону</summary>'
        +fragment(variation['answer'])+
        '<p><strong>Проверка метода:</strong> '+html.escape(variation['reason'])+'</p></details>'
        '<p class="attempt-disclaimer">Самооценка: текстовый ответ не проверяется автоматически; сверяй не только ответ, но и все существенные переходы.</p>'
        '</details>'
    )
    hint_group.insert_after(soup_node(variant_html))
assert len(seen)==25,(len(seen),seen)

heading_levels(problem_soup)
problem_doc=frame(
    '25 задач: условия, подсказки и решения',
    'Условие каждой задачи видно сразу. Подсказки и полное решение скрыты. '
    'Черновик сохраняется только в браузере; автоматической оценки произвольного решения нет.',
    str(problem_soup)
).replace('</body>','<script defer src="./assets/problem-practice.js"></script></body>')
(root/'problems.html').write_text(problem_doc,encoding='utf8')

proof_data=json.loads((root/'_source/proof_workshop.json').read_text(encoding='utf8'))
assert len(proof_data)==11,len(proof_data)
proof_soup=BeautifulSoup(fragment(chunk(10,11)),'html.parser')
seen=set()
for h in list(proof_soup.find_all('h2')):
    m=re.match(r'^(P\d{2})\.',h.get_text(' ',strip=True))
    if not m:continue
    ident=m.group(1)
    assert ident not in seen and ident in proof_data,ident
    seen.add(ident)
    d=proof_data[ident]
    full=proof_soup.new_tag('details')
    full['class']='proof-full'
    summary=proof_soup.new_tag('summary')
    summary.string='Открыть строгое доказательство с полными переходами'
    full.append(summary)
    for node in after_heading_until_next(h):full.append(node.extract())
    h.insert_after(full)
    q_html=[]
    for ix,q in enumerate(d['questions']):
        assert 0<=q['answer']<len(q['options'])
        options=''.join(
            '<button type="button" data-option="'+str(i)+'">'+html.escape(option)+'</button>'
            for i,option in enumerate(q['options'])
        )
        q_html.append('<div class="proof-question" data-answer="'+str(q['answer'])+'" data-explanation="'+html.escape(q['why'],quote=True)+'">'
                      '<p><strong>Шаг '+str(ix+1)+':</strong> '+html.escape(q['prompt'])+'</p>'
                      '<div class="proof-options" role="group" aria-label="Выбери обоснование">'+options+'</div>'
                      '<p class="proof-feedback" aria-live="polite" hidden></p></div>')
    prerequisites=html.escape(d['prerequisites'])
    example=html.escape(d['example'])
    checklist=''.join('<li>'+html.escape(x)+'</li>' for x in d['checklist'])
    workshop=soup_node(
        '<section class="proof-workshop" data-proof="'+ident+'">'
        '<p class="micro">ТРЕНИРОВКА ДО ЧТЕНИЯ ДОКАЗАТЕЛЬСТВА · '+ident+'</p>'
        '<p><strong>Что нужно знать заранее:</strong> '+prerequisites+'</p>'
        '<p><strong>Пример для понимания (не доказательство общего случая):</strong> '+example+'</p>'
        +''.join(q_html)+
        '<label class="proof-write-label" for="proof-write-'+ident+'">Восстанови доказательство своими словами: какие факты используются и почему?</label>'
        '<textarea id="proof-write-'+ident+'" rows="4" placeholder="Попробуй без просмотра эталона…"></textarea>'
        '<details class="proof-rubric"><summary>Критерии ручной самопроверки</summary><ul>'+checklist+'</ul></details>'
        '<p class="attempt-disclaimer">Выбор ответа проверяет только указанный переход, а не умение доказать теорему целиком. Твой текст не оценивается автоматически.</p>'
        '</section>'
    )
    full.insert_before(workshop)
assert len(seen)==11
heading_levels(proof_soup)
proof_doc=frame(
    '11 доказательств: научиться воспроизводить',
    'Сначала восстанови необходимые логические переходы, затем сравни свой текст с доказательством. '
    'Пример на числах не заменяет строгого общего доказательства.',
    str(proof_soup)
).replace('</body>','<script defer src="./assets/proof-practice.js"></script></body>')
(root/'proofs.html').write_text(proof_doc,encoding='utf8')

entries=[]
in_defs=False
for line in source.splitlines():
    if line.startswith('# 9. Все 26'):in_defs=True
    if line.startswith('# 10. Все 11'):in_defs=False
    m=re.match(r'^\*\*(D\d\d)\.\s*(.*?)\*\*',line) if in_defs else None
    if m:entries.append((m.group(1),m.group(2),'Определение'))
    m=re.match(r'^## (P\d\d|T\d\d|№\d+)\.\s*(.*)',line)
    if m:
        ident=m.group(1).replace('№','N')
        group='Доказательство' if ident.startswith('P') else 'Основная задача' if ident.startswith('T') else 'Дополнительная задача'
        entries.append((ident,m.group(2),group))
assert len(entries)==62,entries

def link(e):
    ident,title,g=e
    return ('proofs.html#' if ident[0]=='P' else 'problems.html#' if ident[0] in 'TN' else 'definitions.html#')+ident

def math_title(title):
    if '$' not in title:return html.escape(title)
    s=BeautifulSoup(fragment(title),'html.parser')
    p=s.find('p')
    assert p is not None
    return ''.join(str(v) for v in p.contents)

groups=[('Определения','Определение','defs'),('Доказательства','Доказательство','proofs'),('Основные задачи','Основная задача','main'),('Дополнительные задачи','Дополнительная задача','extra')]
cards=[]
for heading,category,anchor in groups:
    chosen=[x for x in entries if x[2]==category]
    cards.append('<section id="'+anchor+'"><h2>'+heading+' — '+str(len(chosen))+'</h2><div class="catalog">')
    for ident,title,g in chosen:
        cards.append('<a class="catalog-item" href="./'+link((ident,title,g))+'">'
            '<span class="catalog-id">'+ident.replace('N','№')+'</span>'
            '<span>'+math_title(title)+'</span>'
            '<span class="catalog-arrow" aria-hidden="true">↗</span></a>')
    cards.append('</div></section>')
css='''<style>
.book section{margin-bottom:55px}.book section h2{font:500 32px/1.2 Georgia,serif;border-bottom:1px solid #d8dcd2;padding-bottom:15px}
.catalog{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.catalog-item{padding:14px 15px;display:grid;grid-template-columns:50px minmax(0,1fr) 15px;gap:8px;align-items:start;border-radius:7px;background:#f4f7f1;border:1px solid #dce2d9;font-size:13px;text-decoration:none;color:#334b3d;line-height:1.5}
.catalog-item:hover{background:#e6eefc}.catalog-id{font-weight:850;color:#254bb1}.catalog-arrow{color:#254bb1}
@media(max-width:660px){.catalog{grid-template-columns:1fr}.catalog-item{grid-template-columns:43px minmax(0,1fr) 15px}.book section h2{font-size:28px}}
</style>'''
catalog_form=(
    '<div class="catalog-search"><label for="catalog-query">Найти пункт по номеру или названию</label>'
    '<input type="search" id="catalog-query" placeholder="Например: Крамер, ранг, P06, T10" autocomplete="off">'
    '<p id="catalog-count" role="status" aria-live="polite">Показаны все 62 пункта официальной программы.</p>'
    '</div>'
)
css=css.replace('</style>', '.catalog-search{margin:0 0 28px;padding:20px 24px;border:1px solid #d3dfd4;border-radius:8px;background:#f7faf6}.catalog-search label{display:block;margin-bottom:10px;font-size:15px;font-weight:750}.catalog-search input{display:block;width:100%;max-width:650px;min-height:45px;padding:11px 14px;font:inherit;border:1px solid #9faea4;border-radius:5px;background:#fff;color:#234335}.catalog-search input:focus-visible{outline:3px solid #245bd1;outline-offset:2px}.catalog-search p{margin:10px 0 0;font-size:13px;color:#5e7164}.catalog-item[hidden],.book section[hidden]{display:none !important}</style>')
catalog_doc=frame('Все 62 пункта КР №1','Официальный перечень: 26 определений, 11 доказательств, 12 основных и 13 дополнительных задач. Каждый пункт ведёт к учебному материалу. Наличие ссылки не означает доказанного освоения темы.',catalog_form+''.join(cards),css)
catalog_doc=catalog_doc.replace('</body>','<script defer src="./assets/syllabus-filter.js"></script></body>')
(root/'syllabus.html').write_text(catalog_doc,encoding='utf8')

for path,ids in [
    ('proofs.html',['P%02d'%i for i in range(1,12)]),
    ('problems.html',['T%02d'%i for i in range(1,13)]+['N'+str(n) for n in [184,230,231,283,299,302,348,365,853,177,178,586,829]])
]:
    doc=BeautifulSoup((root/path).read_text(encoding='utf8'),'html.parser')
    missing=[ident for ident in ids if not doc.find(id=ident)]
    assert not missing,(path,missing)
print('PAGES:',{p:(root/p).stat().st_size for p in ['proofs.html','problems.html','syllabus.html']},'topics',len(entries))
