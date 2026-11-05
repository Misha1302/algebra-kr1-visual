#!/usr/bin/env python3
"""Reproducibly replace only Chapter 7 in the existing handmade course page.

This file is the canonical owner of Chapter 7 markup. Other chapters, lesson
scripts and the contract of the seven .quickcheck sections must remain intact.
"""
from pathlib import Path
import hashlib
from bs4 import BeautifulSoup

root=Path(__file__).resolve().parents[1]
path=root/'definitions.html'
doc=path.read_text(encoding='utf-8')
start_token='    <section class="chapter" id="chapter-6" aria-labelledby="ch6-title">'
end_token='    </section>\n  </main>'
start=doc.index(start_token)
end=doc.index(end_token,start)+len('    </section>')
old_before=doc[:start]
old_after=doc[end:]

source=(root/'_source/chapter7_content.html').read_text(encoding='utf-8').rstrip()
assert source.startswith(start_token) and source.endswith('</section>')
assert source.count('class="quickcheck"')==1
assert source.count('data-check="advanced"')==1
assert source.count('class="chapter-next"')==1
assert source.count('<section')==1 and source.count('</section>')==1
doc=old_before+source+old_after
css='<link rel="stylesheet" href="./assets/chapter7.css">'
js='<script src="./assets/chapter7.js"></script>'
if css not in doc:
    assert '<link rel="stylesheet" href="./assets/learn.css">' in doc
    doc=doc.replace('<link rel="stylesheet" href="./assets/learn.css">',
                    '<link rel="stylesheet" href="./assets/learn.css">\n'+css,1)
if js not in doc:
    assert '<script src="./assets/transfer-cases.js"></script>' in doc
    doc=doc.replace('<script src="./assets/transfer-cases.js"></script>',js+'\n<script src="./assets/transfer-cases.js"></script>',1)
soup=BeautifulSoup(doc,'html.parser')
chapters=soup.select('section.chapter')
assert len(chapters)==7
assert len(soup.select('.quickcheck'))==7
assert len(soup.select('.formal[id]'))==26
assert len(soup.select('[id="chapter-6"]'))==1
ids=[x.get('id') for x in soup.select('#chapter-6 [id]')]
assert len(ids)==len(set(ids)),ids
path.write_text(doc,encoding='utf-8')
print('CH7_REBUILT',len(source),'bytes',len(ids),'local anchors',
      'protected_before_sha256',hashlib.sha256(old_before.encode()).hexdigest()[:15],
      'protected_after_sha256',hashlib.sha256(old_after.encode()).hexdigest()[:15])
