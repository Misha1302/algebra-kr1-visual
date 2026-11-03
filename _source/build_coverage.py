#!/usr/bin/env python3
"""Evidence-grounded 62-row content coverage snapshot.

Statuses describe affordances, NOT an empirically observed novice learning outcome.
Official titles come from byte-preserved curated reference CSV (see SOURCE_FINGERPRINTS).
"""
import csv
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'_source/official_62_reference.csv'
DEST=ROOT/'docs/remediation/62_COVERAGE_POST_REMEDIATION.csv'
TAGS=['id','type','official_question','official_pdf_location','site_url',
      'formal_statement','plain_explanation','numeric_example','worked_steps',
      'visualization','new_independent_task','answer_validation',
      'mathematical_evidence','coverage_status','pedagogical_validation',
      'remaining_work','priority']
PAGES={name:BeautifulSoup((ROOT/name).read_text(encoding='utf8'),'html.parser')
       for name in ['definitions.html','proofs.html','problems.html','textbook.html']}
with SRC.open(encoding='utf-8-sig',newline='') as fd:original=list(csv.DictReader(fd))
assert len(original)==62,len(original)
rows=[]
for line in original:
    ident=line['id']
    if ident.startswith('E'): ident='N'+ident[1:]
    typ=line['category']
    url='definitions.html#'+ident if typ=='definition' else 'proofs.html#'+ident if typ=='proof' else 'problems.html#'+ident
    page=url.split('#')[0]
    frag=PAGES[page].find(id=ident)
    assert frag is not None,(ident,page)
    content=PAGES[page]
    if typ=='definition':
        chapter=frag.find_parent('section',class_='chapter')
        assert chapter is not None,ident
        assert chapter.select('.worked,.visual'),ident
        rows.append({
            'id':ident,'type':'D','official_question':line['title'],'official_pdf_location':line['official_location'],
            'site_url':url,'formal_statement':'YES','plain_explanation':'CHAPTER_CONTEXT',
            'numeric_example':'CHAPTER_CONTEXT','worked_steps':'CHAPTER_CONTEXT',
            'visualization':'CHAPTER_CONTEXT','new_independent_task':'GROUPED_BY_8_SKILLS',
            'answer_validation':'ONLY_GROUPED_SKILLS','mathematical_evidence':'BASELINE_INVARIANTS; AUDIT_DEFINITION_REVIEW',
            'coverage_status':'EXPLAINED','pedagogical_validation':'NOT_EMPIRICALLY_TESTED',
            'remaining_work':'Individual novice transfer task and counterexample for this exact D-ID not independently graded.',
            'priority':'P2'})
    elif typ=='proof':
        section=content.select_one('.proof-workshop[data-proof="'+ident+'"]')
        assert section is not None and len(section.select('.proof-question'))==2,ident
        rows.append({
            'id':ident,'type':'P','official_question':line['title'],'official_pdf_location':line['official_location'],
            'site_url':url,'formal_statement':'YES','plain_explanation':'PREREQUISITES_AND_EXAMPLE',
            'numeric_example':'YES','worked_steps':'FULL_PROOF_STEPS',
            'visualization':'NOT_APPLICABLE_TO_EVERY_PROOF','new_independent_task':'TWO_STEP_QUESTIONS_AND_FREE_TEXT',
            'answer_validation':'TWO_CHECKED_STEPS; WRITTEN_PROOF_SELF_REVIEW',
            'mathematical_evidence':'BASELINE_PROOF_REVIEW; P06/P10_ADVERSARIAL_SPOT_CHECK',
            'coverage_status':'EXPLAINED','pedagogical_validation':'NOT_EMPIRICALLY_TESTED',
            'remaining_work':'No independent formal grading of full written proof; real novice study not conducted.',
            'priority':'P1'})
    else:
        official=content.select_one('details.solution[data-problem="'+ident+'"]')
        new=content.select_one('.practice-variant[data-variant="'+ident+'"]')
        statement=content.select_one('.problem-statement[role="group"][aria-label="Условие задачи '+ident+'"]')
        assert official and new and statement,(ident,official,new,statement)
        assert new.select_one('.variant-solution') is not None,ident
        rows.append({
            'id':ident,'type':'T' if typ=='main_practice' else 'EXTRA',
            'official_question':line['title'],'official_pdf_location':line['official_location'],
            'site_url':url,'formal_statement':'OFFICIAL_CONDITION_VISIBLE',
            'plain_explanation':'HINTS_AND_COMPLETE_SOLUTION',
            'numeric_example':'YES','worked_steps':'YES',
            'visualization':'SOME_SPECIALIZED_LESSONS','new_independent_task':'ONE_ADDITIONAL_VALIDATED_VARIANT',
            'answer_validation':'MANUAL_SOLUTION_COMPARISON; NO_AUTO_GRADE_OF_FREE_TEXT',
            'mathematical_evidence':'EXACT_SYMPY_VARIANT_ORACLE; BASELINE_MATH_VERIFICATION',
            'coverage_status':'TEACHABLE',
            'pedagogical_validation':'NOT_EMPIRICALLY_TESTED',
            'remaining_work':'New variant is hand-authored, not randomised. Verify individual derivation by self-comparison; novice pilot needed.',
            'priority':'P2'})
assert len(rows)==62 and len({r['id'] for r in rows})==62
DEST.parent.mkdir(parents=True,exist_ok=True)
with DEST.open('w',encoding='utf-8',newline='') as out:
    writer=csv.DictWriter(out,fieldnames=TAGS,lineterminator="\n");writer.writeheader();writer.writerows(rows)
print('COVERAGE:',len(rows),'EXPLAINED:',sum(x['coverage_status']=='EXPLAINED' for x in rows),
      'TEACHABLE content:',sum(x['coverage_status']=='TEACHABLE' for x in rows))
