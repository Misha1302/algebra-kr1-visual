#!/usr/bin/env python3
"""Contract derived from AUD-001/002/005/006/009/010. Does not replace math checks."""
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def html(path):return BeautifulSoup((ROOT/path).read_text(encoding='utf-8'),'html.parser')
def run():
    ps=html('problems.html')
    assert len(ps.select('.problem-statement[role=group]'))==25,"AUD-001: missing public statements"
    assert len(ps.select('details.solution'))==25
    for statement in ps.select('.problem-statement[role=group]'):
        assert len(statement.get_text(' ',strip=True))>45,"Incomplete statement"
    assert len(html('syllabus.html').select('.catalog-item'))==62
    for item in html('syllabus.html').select('.catalog-item'):
        # Invisible MathML <annotation> legitimately contains TeX source for accessibility.
        for annotation in item.select('annotation'):annotation.decompose()
        assert '$' not in item.get_text() and r'\times' not in item.get_text(),"AUD-005: raw visible formula"
    for path in ['problems.html','proofs.html','textbook.html']:
        assert len(html(path).select('h1'))==1,(path,'AUD-006 outline')
    assert html('lab.html').select_one('link[rel=icon]'),"AUD-009 favicon"
    definitions=html('definitions.html')
    assert 'мини-провер' in definitions.select_one('.side-status').get_text(' ',strip=True).lower(),"AUD-002 false completed lessons"
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True)
        p=b.new_page(viewport={'width':1366,'height':900})
        p.goto((ROOT/'problems.html').as_uri())
        assert p.locator('.problem-statement:visible').count()==25,"AUD-001: conditions hidden"
        assert p.locator('details.solution[open]').count()==0
        p.goto((ROOT/'determinants.html').as_uri())
        p.locator('#a').fill('')
        assert p.locator('#det2-error').is_visible(),"AUD-010 empty silently becomes zero"
        p.locator('#a').fill('0')
        assert p.locator('#det2-error').is_hidden(),"AUD-010 valid zero rejected"
        b.close()
    print('PASS remediation contracts')
if __name__=='__main__':run()
