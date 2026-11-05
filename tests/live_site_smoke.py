#!/usr/bin/env python3
"""Real HTTP + browser QA against GitHub Pages (or a local test server).

Crucial: code committed/CI passing != public Pages deployed.
Expected SHA is read from the current checkout, not inferred from workflow success.
Run post-deployment: python tests/live_site_smoke.py --expect-current
"""
from __future__ import annotations
import argparse
import hashlib
import json
import mimetypes
from pathlib import Path
from urllib.parse import urljoin,urlparse
from urllib.request import Request,urlopen
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
PAGES=[
 'index.html','definitions.html','determinants.html','permutations.html','lab.html',
 'textbook.html','proofs.html','problems.html','syllabus.html','practice.html','exam.html'
]
PDFS=[
 'assets/Algebra_KR1_2026_LEFT_TO_RIGHT_FULL.pdf',
 'assets/Algebra_KR1_2026_VISUAL.pdf',
 'assets/KR1_Answer_Key.pdf','assets/KR1_Practice_No_Answers.pdf'
]
STATIC=['favicon.svg','sitemap.xml','robots.txt']

def fetch(base,path):
    url=urljoin(base,path)
    req=Request(url,headers={'User-Agent':'AlgebraKR1-DeploymentQA/1.0','Cache-Control':'no-cache'})
    with urlopen(req,timeout=20) as res:
        return res.getcode(),res.headers.get('Content-Type',''),res.read(),res.geturl()

def discover_assets(doc):
    assets=[]
    for link in doc.find_all('link',href=True):
        href=link['href']
        if link.get('rel') and any(x in link['rel'] for x in ['stylesheet','icon']):
            assets.append(href)
    for script in doc.find_all('script',src=True):assets.append(script['src'])
    return assets

def run(base,expect_current,browser,out):
    out.mkdir(parents=True,exist_ok=True)
    base=base.rstrip('/')+'/'
    reports=[]
    targets={x for x in PAGES+PDFS+STATIC}
    errors=[]
    for name in PAGES:
        code,mime,data,url=fetch(base,name)
        if code!=200:errors.append(f'{name}: HTTP {code}')
        if 'html' not in mime:errors.append(f'{name}: MIME {mime!r} expected HTML')
        doc=BeautifulSoup(data,'html.parser')
        if not doc.select('h1'):errors.append(f'{name}: missing H1')
        for uri in discover_assets(doc):
            parsed=urlparse(uri)
            if parsed.scheme or parsed.netloc:continue
            path=(Path(name).parent/parsed.path).as_posix().removeprefix('./')
            if path not in targets:targets.add(path)
        reports.append({'path':name,'status':code,'mime':mime,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'url':url})
    for name in sorted(targets-set(PAGES)):
        code,mime,data,url=fetch(base,name)
        if code!=200:errors.append(f'{name}: HTTP {code}')
        suffix=Path(name).suffix
        if suffix=='.pdf':
            if 'pdf' not in mime.lower():errors.append(f'{name}: MIME {mime!r} expected application/pdf')
            if not data.startswith(b'%PDF-'):errors.append(f'{name}: invalid PDF signature')
        elif suffix=='.css' and 'css' not in mime.lower():errors.append(f'{name}: wrong CSS MIME {mime}')
        elif suffix=='.js' and ('javascript' not in mime.lower() and 'ecmascript' not in mime.lower()):
            errors.append(f'{name}: wrong JS MIME {mime}')
        elif suffix=='.svg' and 'svg' not in mime.lower():errors.append(f'{name}: wrong SVG MIME {mime}')
        reports.append({'path':name,'status':code,'mime':mime,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'url':url})
    if expect_current:
        for item in reports:
            local=ROOT/item['path']
            if not local.is_file():errors.append('local file missing: '+str(local));continue
            digest=hashlib.sha256(local.read_bytes()).hexdigest()
            item['matches_checkout']=item['sha256']==digest
            if not item['matches_checkout']:errors.append('SHA drift: '+item['path'])
    if browser:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            for width in [390,768,1366,1920]:
                paths=PAGES if width==1366 else ['index.html','definitions.html','practice.html','exam.html']
                for name in paths:
                    page=browser.new_page(viewport={'width':width,'height':900})
                    bad=[]
                    page.on('pageerror',lambda e:bad.append('PAGEERROR '+str(e)))
                    page.on('response',lambda r:bad.append('HTTP '+str(r.status)+' '+r.url) if r.status>=400 else None)
                    page.goto(urljoin(base,name),wait_until='load',timeout=30000)
                    page.wait_for_timeout(100)
                    dim=page.evaluate('({w:document.documentElement.scrollWidth,c:document.documentElement.clientWidth})')
                    if dim['w']>dim['c']+3:bad.append('HORIZONTAL_OVERFLOW '+repr(dim))
                    if name=='definitions.html':
                        if page.locator('#chapter-6 .ch7-workshop').count()!=3:
                            bad.append('missing chapter 7 LU/skeleton/recurrence workshops')
                        if page.locator('#ch7-lu-count').inner_text()!='Шаг 1 из 4':
                            bad.append('chapter 7 initial LU state missing')
                        page.locator('#ch7-lu-next').click()
                        if page.locator('#ch7-lu-count').inner_text()!='Шаг 2 из 4':
                            bad.append('chapter 7 LU next button failed')
                        page.locator('#ch7-rec-n').fill('4')
                        if not page.locator('#ch7-rec-equation').inner_text().endswith('= 211.'):
                            bad.append('chapter 7 recurrence wrong')
                    if name=='practice.html':
                        if page.locator('.transfer-practice[data-transfer]').count()!=8:bad.append('missing independent exercises')
                    if name=='proofs.html':
                        if page.locator('.proof-workshop').count()!=11:bad.append('missing proof workshops')
                    if name=='problems.html':
                        if page.locator('.problem-statement[role=group]:visible').count()!=25:bad.append('hidden official conditions')
                    if bad:errors.extend([f'{name}@{width}: '+msg for msg in bad])
                    reports.append({'browser':name,'width':width,'errors':bad,'dimensions':dim})
                    page.close()
            browser.close()
    verdict={'base':base,'files_checked':sum('path' in x for x in reports),
             'page_checks':len([x for x in reports if 'browser' in x]),
             'errors':errors,'results':reports}
    (out/'live_site_results.json').write_text(json.dumps(verdict,ensure_ascii=False,indent=2),encoding='utf8')
    print('LIVE QA:',base,'files:',verdict['files_checked'],'browser passes:',verdict['page_checks'],'errors:',len(errors))
    for error in errors:print('  FAIL',error)
    assert not errors,'Live deployment QA failed; see '+str(out/'live_site_results.json')
    print('PASS Live HTML, CSS, JS, 4 PDFs, SHA consistency and browser tests.')
    return verdict

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--base',default='https://misha1302.github.io/algebra-kr1-visual/')
    parser.add_argument('--expect-current',action='store_true')
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--output',default='/tmp/algebra-kr1-live-qa')
    args=parser.parse_args()
    run(args.base,args.expect_current,not args.no_browser,Path(args.output))
