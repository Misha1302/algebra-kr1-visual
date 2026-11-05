#!/usr/bin/env python3
"""Browser acceptance: three Chapter 7 methods, actual interactions and responsive layout."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from sympy import Matrix
import json

ROOT=Path(__file__).resolve().parents[1]
FILE=(ROOT/'definitions.html').as_uri()
SHOTS=ROOT/'docs/chapter7-review'
SHOTS.mkdir(parents=True,exist_ok=True)

def openpage(page):
    page.goto(FILE+'#chapter-6',wait_until='load',timeout=30000)
    page.add_style_tag(content='html{scroll-behavior:auto!important}*{animation-duration:0s!important;transition-duration:0s!important}')
    page.evaluate("window.scrollTo(0,document.getElementById('chapter-6').getBoundingClientRect().top + window.scrollY)")
    page.wait_for_timeout(160)

def viewport_screenshot(page,selector,destination):
    page.evaluate("""selector => {
        const x=document.querySelector(selector);
        document.documentElement.style.scrollBehavior='auto';
        window.scrollTo(0,x.getBoundingClientRect().top+window.scrollY-10);
    }""",selector)
    page.wait_for_timeout(150)
    page.screenshot(path=str(SHOTS/destination),full_page=False,animations='disabled')

def check():
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        errors=[]
        page=browser.new_page(viewport={'width':1366,'height':900})
        page.on('pageerror',lambda error:errors.append('desktop:'+str(error)))
        openpage(page)
        assert page.locator('#chapter-6').is_visible()
        assert page.locator('#chapter-6 .ch7-topic').count()==4
        assert page.locator('#chapter-6 .ch7-teaching-steps').count()==3
        assert page.locator('#ch7-lu-workshop table').count()==1
        assert page.locator('#ch7-lu-count').inner_text()=='Шаг 1 из 4'
        assert '4 под двойкой' in page.locator('#ch7-lu-reason').inner_text()
        viewport_screenshot(page,'#chapter-6','after_chapter7_top_1366.png')
        viewport_screenshot(page,'#ch7-lu','after_lu_1366.png')
        for i in range(2,5):
            page.locator('#ch7-lu-next').click()
            assert page.locator('#ch7-lu-count').inner_text()==f'Шаг {i} из 4'
        assert page.locator('#ch7-lu-next').is_disabled()
        assert 'L·U' in page.locator('#ch7-lu-reason').inner_text()
        assert page.locator('#ch7-lu-matrix td').all_inner_texts()==['1','0','2','1']
        page.locator('#ch7-lu-prev').focus()
        page.keyboard.press('Enter')
        assert page.locator('#ch7-lu-count').inner_text()=='Шаг 3 из 4'
        assert page.locator('#ch7-lu-matrix td').all_inner_texts()==['2','1','0','3']
        page.locator('#ch7-lu-reset').click()
        assert page.locator('#ch7-lu-count').inner_text()=='Шаг 1 из 4'
        assert page.locator('#ch7-lu-prev').is_disabled()
        page.locator('#ch7-lu-check').click()
        assert page.locator('#ch7-lu-feedback').is_visible()
        assert page.locator('#ch7-lu-feedback').evaluate('(e)=>e.classList.contains("ch7-error")')
        page.locator('#ch7-lu-k').fill('2')
        page.locator('#ch7-lu-u22').fill('5')
        page.locator('#ch7-lu-check').click()
        assert 'Множитель найден верно' in page.locator('#ch7-lu-feedback').inner_text()
        page.locator('#ch7-lu-u22').fill('3')
        page.locator('#ch7-lu-check').click()
        assert 'Оба шага верны' in page.locator('#ch7-lu-feedback').inner_text()
        assert page.locator('#ch7-lu-k').get_attribute('aria-invalid')=='false'
        assert page.locator('#ch7-lu-u22').get_attribute('aria-invalid')=='false'
        for column,phrase in [(0,'(1,0)'),(1,'(0,1)'),(2,'(1,1)')]:
            page.locator(f'[data-ch7-column="{column}"]').click()
            assert phrase in page.locator('#ch7-skeleton-explain').inner_text()
            assert page.locator(f'[data-ch7-column="{column}"]').get_attribute('aria-pressed')=='true'
        viewport_screenshot(page,'#ch7-skeleton','after_skeleton_1366.png')
        page.locator('#ch7-sk-a').fill('2')
        page.locator('#ch7-sk-b').fill('3')
        page.locator('#ch7-sk-check').click()
        assert 'α=2, β=3' in page.locator('#ch7-sk-feedback').inner_text()
        cases={'base':{2:19,3:65,4:211,5:665,6:2059},
               'second':{2:14,3:48,4:164,5:560,6:1912}}
        for preset,expected in cases.items():
            page.locator('#ch7-rec-preset').select_option(preset)
            for n,val in expected.items():
                page.locator('#ch7-rec-n').fill(str(n))
                actual=page.locator('#ch7-rec-equation').inner_text()
                assert actual.endswith('= '+str(val)+'.'),(preset,n,val,actual)
                assert page.locator('#ch7-rec-matrix td').count()==n*n
        viewport_screenshot(page,'#ch7-recurrence','after_recurrence_1366.png')
        page.locator('#ch7-rec-d2').fill('14')
        page.locator('#ch7-rec-d3').fill('0')
        page.locator('#ch7-rec-check').click()
        assert 'D₂ верен' in page.locator('#ch7-rec-feedback').inner_text()
        page.locator('#ch7-rec-d3').fill('48')
        page.locator('#ch7-rec-check').click()
        assert 'Верно' in page.locator('#ch7-rec-feedback').inner_text()
        # These newly introduced exercises do not write false mastery records.
        assert page.evaluate("localStorage.getItem('algebra-kr1-independent-verified-v1')")==None
        assert page.evaluate("localStorage.getItem('algebra-kr1-mini-checks-v2')")==None

        responsive=[]
        for width in [300,320,360,390,768,1366,1920]:
            mobile=browser.new_page(viewport={'width':width,'height':850})
            mobile.on('pageerror',lambda e:errors.append(f'{width}:'+str(e)))
            openpage(mobile)
            assert mobile.locator('#ch7-lu-matrix table').count()==1
            assert mobile.locator('#ch7-rec-matrix table').count()==1
            dims=mobile.evaluate("""()=>({
                width:document.documentElement.clientWidth,
                scroll:document.documentElement.scrollWidth,
                chapter:Math.round(document.getElementById('chapter-6').getBoundingClientRect().width),
                viewport:innerWidth
            })""")
            assert dims['scroll']<=dims['width']+3,(width,dims)
            assert dims['chapter']<=width+3,(width,dims)
            # Regression for native-select intrinsic-width divergence between Chromium builds.
            select_right=mobile.locator('#ch7-rec-preset').evaluate('(e)=>e.getBoundingClientRect().right')
            assert select_right<=width+1,(width,select_right)
            for target in ['#ch7-lu','#ch7-skeleton','#ch7-recurrence']:
                mobile.evaluate("selector=>document.querySelector(selector).scrollIntoView({behavior:'instant',block:'start'})",target)
                assert mobile.locator(target+' h3').first.is_visible()
            if width in [390,768]:
                viewport_screenshot(mobile,'#ch7-lu',f'after_lu_{width}.png')
                viewport_screenshot(mobile,'#ch7-skeleton',f'after_skeleton_{width}.png')
                viewport_screenshot(mobile,'#ch7-recurrence',f'after_recurrence_{width}.png')
            responsive.append(dims)
            mobile.close()
        assert not errors,errors
        (SHOTS/'acceptance.json').write_text(json.dumps({
            'screenshots':[p.name for p in sorted(SHOTS.glob('after_*.png'))],
            'widths':responsive,'live_errors':errors,
            'method_count':3,'interactive_workshops':3,'independent_problems':3,
            'mathematical_checks':'SymPy in chapter7_math_oracle.py'
        },ensure_ascii=False,indent=2),encoding='utf8')
        browser.close()
    print('PASS Chapter 7 E2E: LU step navigation and keyboard, 3 separate feedback exercises, skeleton reconstruction, two recurrence series, responsive widths 300..1920, zero browser errors')
if __name__=='__main__':check()
