from playwright.sync_api import sync_playwright
from pathlib import Path
import os,json
root=Path(__file__).resolve().parents[1]
js=os.environ.get('AXE_JS_PATH','/tmp/algebra-kr1-axe/node_modules/axe-core/axe.min.js')
files=['index.html','definitions.html','practice.html','exam.html','problems.html','proofs.html','syllabus.html','determinants.html','permutations.html','lab.html','textbook.html']
out=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for f in files:
  for width in ([390,1366] if f in ['index.html','definitions.html','practice.html','exam.html','problems.html','proofs.html'] else [1366]):
   page=browser.new_page(viewport={'width':width,'height':900})
   try:
    page.goto((root/f).as_uri(),wait_until='load',timeout=24000)
    page.add_script_tag(path=js)
    results=page.evaluate('''async()=>await axe.run(document,{runOnly:{type:"tag",values:["wcag2a","wcag2aa","wcag21a","wcag21aa"]}})''')
    issues=[]
    for v in results['violations']:
     issues.append({'id':v['id'],'impact':v['impact'],'nodes':len(v['nodes']),
                    'sample':[n['target'] for n in v['nodes'][:4]],'description':v['help']})
    out.append({'file':f,'width':width,'violation_count':len(issues),'violations':issues})
    print(f,width,'violations:',[(e['id'],e['impact'],e['nodes']) for e in issues],flush=True)
   except Exception as e:
    out.append({'file':f,'width':width,'error':str(e)})
    print('ERROR',f,width,repr(e),flush=True)
   page.close()
 browser.close()
(root/'docs/remediation/axe_audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))

violations=[entry for entry in out if entry.get("violations") or entry.get("error")]
print("WCAG accessible pages:",len(out),"audited, failures:",len(violations))
assert not violations, violations
