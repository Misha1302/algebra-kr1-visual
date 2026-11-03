from pathlib import Path
import re,math
from urllib.parse import urlsplit,unquote
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=['index.html','definitions.html','lab.html','determinants.html','permutations.html','syllabus.html','proofs.html','problems.html','textbook.html']
EXPECTED=['D%02d'%i for i in range(1,27)]+['P%02d'%i for i in range(1,12)]+['T%02d'%i for i in range(1,13)]+['N'+str(i) for i in [184,230,231,283,299,302,348,365,853,177,178,586,829]]
def open_page(page,name):
 page.goto((ROOT/name).as_uri(),wait_until='load',timeout=60000)
 page.wait_for_timeout(150)
def assert_no_overflow(page,name):
 w=page.evaluate("({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth})")
 assert w['scroll']<=w['width']+3,(name,w)
def static_checks():
 count=0
 cache={}
 for f in HTML:
  soup=BeautifulSoup((ROOT/f).read_text(),'html.parser')
  assert soup.title,(f,'title')
  for a in soup.find_all('a',href=True):
   h=a['href'];parts=urlsplit(h)
   if parts.scheme or h.startswith('//') or h.startswith('mailto:'):continue
   target=(ROOT/parts.path.lstrip('./')).resolve() if parts.path else (ROOT/f)
   assert target.exists(),(f,h,'broken path')
   if parts.fragment and target.suffix=='.html':
    s=cache.setdefault(str(target),BeautifulSoup(target.read_text(),'html.parser'))
    if s.find(id=unquote(parts.fragment)) is None:
     # Dynamic hash routes in lab are tab names and are allowed.
     assert target.name=='lab.html' and parts.fragment in ['matrix','dimensions','transpose','gauss','adj','rank','factor','quiz'],(f,h,'missing anchor')
   count+=1
 t=BeautifulSoup((ROOT/'textbook.html').read_text(),'html.parser')
 for id in EXPECTED:assert t.find(id=id),(id,'missing in textbook')
 for p,ids in [('proofs.html',[i for i in EXPECTED if i.startswith('P')]),('problems.html',[i for i in EXPECTED if i.startswith(('T','N'))])]:
  t=BeautifulSoup((ROOT/p).read_text(),'html.parser')
  for id in ids:assert t.find(id=id),(p,id,'missing')
 assert BeautifulSoup((ROOT/'problems.html').read_text(),'html.parser').select('details.solution')
 print('STATIC:',len(EXPECTED),'official anchors; validated',count,'internal links')
def run():
 static_checks()
 with sync_playwright() as pw:
  b=pw.chromium.launch(headless=True)
  p=b.new_page(viewport={'width':1365,'height':860},device_scale_factor=1)
  errs=[]
  p.on('pageerror',lambda e:errs.append(str(e)))
  open_page(p,'index.html')
  assert p.locator('a[href="./determinants.html"]').count()>=1
  assert p.locator('a[href="./permutations.html"]').count()>=1
  assert_no_overflow(p,'homepage desktop')
  open_page(p,'determinants.html')
  assert '= 5' in p.locator('#det2-result').inner_text()
  p.locator('#a').fill('3')
  assert '= 9' in p.locator('#det2-result').inner_text()
  p.locator('#det2-singular').click()
  assert '= 0' in p.locator('#det2-result').inner_text()
  for val in ['r0','r1','r2','c0','c1','c2']:
   p.locator('#expand-axis').select_option(val)
   assert '= 22' in p.locator('#laplace-total').inner_text(),('laplace',val,p.locator('#laplace-total').inner_text())
   for i in range(2):
    p.locator('#lap-next').click()
    assert '= 22' in p.locator('#laplace-total').inner_text()
  assert p.locator('#perm-det-options button').count()==6
  p.locator('#perm-det-options button').nth(3).click()
  assert 'Вклад: 10' in p.locator('#perm-det-work').inner_text()
  p.locator('button[data-rowop="swap"]').click()
  assert '−5' in p.locator('#rowop-result').inner_text()
  p.locator('button[data-rowop="add"]').click()
  assert 'Определитель не изменился' in p.locator('#rowop-result').inner_text()
  p.locator('#rec-n').fill('5')
  assert 'D5 = 665' in p.locator('#rec-result').inner_text()
  assert_no_overflow(p,'determinants desktop')
  p.screenshot(path='/tmp/kr1-full-determinants-desktop.png',full_page=True)
  open_page(p,'permutations.html')
  assert 'τ(σ(i))' in p.locator('#product .mathblock').first.inner_text()
  assert '→ 3' in p.locator('#comp-path').inner_text()
  p.locator('#reverse').click()
  assert '→ 2' in p.locator('#comp-path').inner_text()
  p.locator('#inv-options button').first.click()
  assert 'Количество: 3' in p.locator('#inv-result').inner_text()
  for i in range(1,8):
   p.locator('#task178-options button[data-value="'+str(i)+'"]').click()
   assert 'Все 7 значений: совпадают' in p.locator('#task178-check').inner_text()
  v=p.evaluate('window.__algebraPermutationVerification')
  assert v['check'] is True and v['X']==[7,1,2,3,4,5,6],v
  assert_no_overflow(p,'permutations desktop')
  p.screenshot(path='/tmp/kr1-full-permutations-desktop.png',full_page=True)
  open_page(p,'syllabus.html')
  assert p.locator('.catalog-item').count()==62,p.locator('.catalog-item').count()
  assert_no_overflow(p,'syllabus desktop')
  open_page(p,'problems.html')
  assert p.locator('details.solution').count()==25,p.locator('details.solution').count()
  assert p.locator('details.solution[open]').count()==0
  p.locator('details.solution').first.locator('summary').click()
  assert p.locator('details.solution[open]').count()==1
  assert_no_overflow(p,'problems desktop')
  open_page(p,'proofs.html')
  assert_no_overflow(p,'proofs desktop')
  open_page(p,'textbook.html')
  assert p.locator('#N178').count()==1
  assert p.locator('math').count()>1000
  assert_no_overflow(p,'textbook desktop')
  mobile=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
  mobile.on('pageerror',lambda e:errs.append('MOBILE '+str(e)))
  for name in HTML:
   open_page(mobile,name)
   assert_no_overflow(mobile,name+' mobile')
  for name in ['determinants.html','permutations.html','index.html']:
   open_page(mobile,name)
   mobile.screenshot(path='/tmp/kr1-full-'+name.replace('.html','')+'-mobile.png',full_page=True)
  assert not errs,errs
  print('PASS: determinant 2x2/3x3 all rows and columns, six Leibniz choices, invariants, recurrence, permutations, №178, all 62, desktop/mobile, no JS errors')
  b.close()
if __name__=='__main__':run()
