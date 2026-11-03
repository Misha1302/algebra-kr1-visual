#!/usr/bin/env python3
"""Pedagogical, mathematical and mobile acceptance checks of definitions.html."""
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[1]
file=(BASE/'definitions.html').as_uri()
def check():
    soup=BeautifulSoup((BASE/'definitions.html').read_text(),'html.parser')
    expected=['D%02d'%i for i in range(1,27)]
    missing=[id for id in expected if soup.find(id=id) is None]
    assert not missing,missing
    assert len(soup.select('section.chapter'))==7
    assert len(soup.select('.quickcheck'))==7
    assert len(soup.select('.formal[id]'))==26
    print('CONTENT: 7 chapters, 26 formal definitions, 7 knowledge checks')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        p=browser.new_page(viewport={'width':1400,'height':950},device_scale_factor=1)
        errors=[]
        p.on('pageerror',lambda e:errors.append(str(e)))
        p.goto(file,wait_until='load')
        assert p.locator('#base-explain').inner_text().endswith('a₂₃ = 6.')
        p.locator('#base-matrix button[data-i="0"][data-j="1"]').click()
        assert 'a₁₂ = 2' in p.locator('#base-explain').inner_text()
        p.locator('#mul-C button[data-i="0"][data-j="1"]').click()
        for _ in range(3):p.locator('#mul-next').click()
        assert p.locator('#mul-equation').inner_text().endswith('= 64')
        assert p.locator('#mul-next').is_disabled()
        p.locator('#mul-restart').click()
        assert '1, 2, 3' in p.locator('#mul-equation').inner_text()
        p.locator('#size-bad').click()
        assert 'не определено' in p.locator('#size-visual').inner_text()
        p.locator('#size-ok').click()
        assert 'Совместимо' in p.locator('#size-visual').inner_text()
        p.locator('#tr-A button[data-i="1"][data-j="2"]').click()
        assert 'из (2,3) в (3,2)' in p.locator('#tr-caption').inner_text()
        for _ in range(3):p.locator('#gauss-next').click()
        assert 'x = 1, y = 2' in p.locator('#gauss-why').inner_text()
        assert p.locator('#gauss-next').is_disabled()
        p.locator('#gauss-reset').click()
        assert '2x−y=0' in p.locator('#gauss-equation').inner_text()
        p.locator('#permutation-points button[data-p="3"]').click()
        assert 'σ(3)=1' in p.locator('#permutation-caption').inner_text()
        assert 'C' in p.locator('#cofactor-caption').inner_text()
        assert '=5.' in p.locator('#cofactor-caption').inner_text().replace(' ','') or 'C=5.' in p.locator('#cofactor-caption').inner_text().replace(' ','')
        p.locator('#cofactor-A button[data-i="1"][data-j="1"]').click()
        assert 'C=3.' in p.locator('#cofactor-caption').inner_text().replace(' ','')
        for _ in range(4):p.locator('#inverse-next').click()
        assert 'единичную матрицу' in p.locator('#inverse-caption').inner_text()
        p.locator('#inverse-reset').click()
        assert 'det A = 2·4' in p.locator('#inverse-caption').inner_text()
        p.locator('#rank-t').fill('1')
        assert p.locator('#rank-answer').inner_text()=='rank A = 2'
        assert p.locator('#rank-det').inner_text().endswith('= 1')
        p.locator('#rank-zero').click()
        assert p.locator('#rank-answer').inner_text()=='rank A = 1'
        p.locator('#system-controls button[data-system="none"]').click()
        assert 'rank A = 1, rank[A|b] = 2' in p.locator('#system-verdict').inner_text()
        assert p.locator('#system-verdict').evaluate('(el)=>el.classList.contains("bad")')
        p.locator('#system-controls button[data-system="one"]').click()
        assert 'Единственное решение' in p.locator('#system-verdict').inner_text()
        p.locator('#system-controls button[data-system="many"]').click()
        assert 'бесконечно много' in p.locator('#system-verdict').inner_text()
        for chapter in ['matrix','gauss','det','inverse','rank','systems','advanced']:
            quiz=p.locator('.quickcheck[data-check="'+chapter+'"]')
            quiz.locator('button[data-answer="bad"]').first.click()
            assert quiz.locator('.feedback').is_visible()
            assert 'bad' in quiz.locator('.feedback').get_attribute('class')
            quiz.locator('button[data-answer="yes"]').click()
            assert 'bad' not in quiz.locator('.feedback').get_attribute('class')
        assert p.locator('#chapter-progress').inner_text()=='7/7'
        p.reload(wait_until='load')
        assert p.locator('#chapter-progress').inner_text()=='7/7'
        p.screenshot(path='/tmp/kr1-new-learning-desktop.png',full_page=True)
        print('INTERACTIONS: matrices, row/col, transpose, Gauss, cofactors, inverse, ranks, systems, seven quizzes')
        for w in [390,768,1440]:
            mobile=browser.new_page(viewport={'width':w,'height':820})
            mobile.on('pageerror',lambda e:errors.append('width='+str(w)+': '+str(e)))
            mobile.goto(file,wait_until='load')
            dims=mobile.evaluate('({outer:document.documentElement.scrollWidth,inner:document.documentElement.clientWidth})')
            assert dims['outer']<=dims['inner']+3,(w,dims)
            assert mobile.locator('#D26').count()==1
            if w==390:mobile.screenshot(path='/tmp/kr1-new-learning-mobile.png',full_page=True)
            mobile.close()
        assert not errors,errors
        print('PASS: no horizontal overflow at 390/768/1440, no browser JS errors, all 26 anchors')
        browser.close()
if __name__=='__main__':check()
