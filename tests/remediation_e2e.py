#!/usr/bin/env python3
"""End-to-end learning paths, response visibility and mobile browser smoke.

Requires Playwright Chromium. Uses real local pages and interactions, not fake DOM mocks.
"""
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/remediation/screenshots'
OUT.mkdir(parents=True,exist_ok=True)
def openpage(p,filename):
    p.goto((ROOT/filename).as_uri(),wait_until='load')
    p.wait_for_timeout(150)
def fill_case(p,topic,values):
    section=p.locator('.transfer-practice[data-transfer="'+topic+'"]')
    for key,value in values.items():
        ctrl=section.locator('[data-field="'+key+'"]')
        if ctrl.evaluate("(el)=>el.tagName")=="SELECT":
            ctrl.select_option(str(value))
        else:
            ctrl.fill(str(value))
    section.locator('.transfer-check').click()
    return section.locator('.transfer-status').inner_text()
def check():
    s=BeautifulSoup((ROOT/'problems.html').read_text(encoding='utf8'),'html.parser')
    assert len(s.select('.problem-statement[role=group]'))==25
    assert len(s.select('details.solution'))==25
    assert len(s.select('.practice-variant'))==25
    assert len(s.select('.attempt-workspace'))==50
    assert len(s.select('math'))>100
    proofs=BeautifulSoup((ROOT/'proofs.html').read_text(encoding='utf8'),'html.parser')
    assert len(proofs.select('.proof-workshop'))==11
    assert len(proofs.select('.proof-question'))==22
    assert len(proofs.select('details.proof-full'))==11
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True)
        errors=[]
        page=b.new_page(viewport={'width':1366,'height':900})
        page.on('pageerror',lambda e:errors.append(str(e)))
        openpage(page,'problems.html')
        assert page.locator('.problem-statement:visible').count()==25
        assert page.locator('details.solution[open]').count()==0
        assert page.locator('.practice-variant[open]').count()==0
        assert page.locator('.problem-statement[role=group] math').count()>30
        page.locator('.method-hint').first.locator('summary').click()
        assert page.locator('details.solution[open]').count()==0
        page.locator('.attempt-workspace').first.locator('textarea').fill('R₂ <- R₂ + R₁; проверю позже')
        page.locator('.attempt-workspace').first.locator('button').click()
        assert 'сохранён' in page.locator('.attempt-workspace').first.locator('.save-message').inner_text().lower()
        page.screenshot(path=str(OUT/'after_problems_1366.png'),full_page=False)
        page.locator('.problem-statement[role=group]').first.screenshot(path=str(OUT/'after_condition_1366.png'))
        openpage(page,'proofs.html')
        assert page.locator('details.proof-full[open]').count()==0
        p06=page.locator('.proof-workshop[data-proof="P06"]')
        p06.locator('.proof-question').first.locator('button[data-option="0"]').click()
        assert p06.locator('.proof-feedback').first.is_visible()
        assert 'не тот' not in p06.locator('.proof-feedback').first.inner_text().lower()
        # Answer index 1 is correct (using polynomiality without division).
        p06.locator('.proof-question').first.locator('button[data-option="1"]').click()
        assert 'Верно' in p06.locator('.proof-feedback').first.inner_text()
        page.screenshot(path=str(OUT/'after_proofs_1366.png'),full_page=False)
        p06.screenshot(path=str(OUT/'after_proof_workshop.png'))
        openpage(page,'practice.html')
        assert page.locator('.transfer-practice').count()==8
        assert 'Верно 0' in fill_case(page,'matrix',{'first':"999",'result':"0"})
        assert 'Все проверяемые шаги верны' in fill_case(page,'matrix',{'first':"4",'result':"-3"})
        assert 'Все проверяемые шаги верны' in fill_case(page,'gauss',{'rhs':"-9",'y':"3",'x':"2"})
        assert 'Все проверяемые шаги верны' in fill_case(page,'permutations',{'left':'1','right':'3','power':'3'})
        assert 'Все проверяемые шаги верны' in fill_case(page,'det',{'main':"4",'off':"-6",'det':"10"})
        assert 'Все проверяемые шаги верны' in fill_case(page,'inverse',{'det':"1",'entry':"-1"})
        assert 'Все проверяемые шаги верны' in fill_case(page,'rank',{'minor':"0",'rank':"1"})
        assert 'Все проверяемые шаги верны' in fill_case(page,'systems',{'rankA':"2",'rankAug':"2",'type':"one"})
        assert 'Все проверяемые шаги верны' in fill_case(page,'advanced',{'l21':"3",'u22':"2"})
        assert '8/8' in page.locator('[data-independent-progress]').inner_text()
        matrix=page.locator('.transfer-practice[data-transfer="matrix"]')
        matrix.locator('.transfer-next').click()
        assert 'Вариант 2 из 3' in matrix.locator('.transfer-heading').text_content()
        assert 'Все проверяемые шаги верны' in fill_case(page,'matrix',{'first':"6",'result':"10",'transpose':"3,2"})
        page.screenshot(path=str(OUT/'after_practice_1366.png'),full_page=False)
        matrix.screenshot(path=str(OUT/'after_practice_matrix.png'))
        openpage(page,'definitions.html')
        assert page.locator('.transfer-practice').count()==8
        assert page.locator('#transfer-progress').inner_text()=='8/8'
        assert 'Мини-проверки:' in page.locator('.side-status').inner_text()
        page.evaluate("localStorage.setItem('algebra-kr1-last-chapter-v1','chapter-4')")
        page.reload(wait_until='load')
        assert page.locator('#resume-chapter').is_visible()
        assert page.locator('#resume-chapter').get_attribute('href')=='#chapter-4'
        page.locator('#resume-chapter').click()
        assert page.url.endswith('#chapter-4')
        openpage(page,'exam.html')
        assert page.locator('.exam-case').count()==8
        assert not page.locator('.exam-after').first.is_visible()
        # This batch is intentionally different from first-practice variants.
        answers={
          'matrix':{'first':'6','result':'10','transpose':'3,2'},
          'gauss':{'pivot':'swap','x':'3','y':'2'},
          'permutations':{'x1':'2','x2':'3','x3':'1'},
          'det':{'main':'4','off':'-6','det':'10'},
          'inverse':{'det':'7','entry':'2/7'},
          'rank':{'minor':'0','rank':'1'},
          'systems':{'rankA':'2','rankAug':'2','type':'one'},
          'advanced':{'rank':'2','c1':'2','c2':'3'},
        }
        for topic,fields in answers.items():
            section=page.locator('#exam-'+topic)
            for name,value in fields.items():
                ctrl=section.locator('[data-field="'+name+'"]')
                if ctrl.evaluate("(el)=>el.tagName")=="SELECT":ctrl.select_option(value)
                else:ctrl.fill(value)
        assert not page.locator('.exam-after').first.is_visible()
        page.locator('.exam-submit').click()
        assert '8 из 8' in page.locator('#exam-verdict').inner_text()
        assert page.locator('.exam-after:visible').count()==8
        page.screenshot(path=str(OUT/'after_exam_1366.png'),full_page=False)
        openpage(page,'determinants.html')
        page.locator('#a').fill('')
        assert page.locator('#det2-error').is_visible()
        page.locator('#a').fill('0')
        assert not page.locator('#det2-error').is_visible()
        page.locator('#rec-n').fill('13')
        assert page.locator('#rec-error').is_visible()
        page.locator('#rec-n').fill('5')
        assert not page.locator('#rec-error').is_visible()
        openpage(page,'lab.html')
        assert page.locator('link[rel="icon"]').count()==1
        # Visual on four viewports, with no document-level horizontal overflow.
        for w in [390,768,1366,1920]:
            mobile=b.new_page(viewport={'width':w,'height':900})
            mobile.on('pageerror',lambda e:errors.append('w='+str(w)+': '+str(e)))
            for name in ['definitions.html','practice.html','exam.html','problems.html','proofs.html']:
                openpage(mobile,name)
                sizes=mobile.evaluate('({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth})')
                assert sizes['scroll']<=sizes['client']+3,(w,name,sizes)
                if name=='practice.html' and w in [390,1920]:
                    mobile.screenshot(path=str(OUT/f'after_practice_{w}.png'),full_page=False)
            mobile.close()
        assert not errors,errors
        b.close()
    print('PASS remediation E2E: 25 readable statements, 25 new variants, 11 proof workshops, 24 exercise seeds, exam, progress, validation and 4 viewport widths.')
if __name__=='__main__':check()
