#!/usr/bin/env python3
"""Independent exact-arithmetic oracle for Chapter 7, including official T11/T12/T08.

The oracle must not use a value computed by chapter7.js as its expectation.
"""
from itertools import product
from pathlib import Path
from random import Random
from fractions import Fraction
from bs4 import BeautifulSoup
from sympy import Matrix, Rational, zeros, eye
import json,hashlib

ROOT=Path(__file__).resolve().parents[1]
DOC=BeautifulSoup((ROOT/'definitions.html').read_text(encoding='utf-8'),'html.parser')
SECTION=DOC.select_one('#chapter-6')
assert SECTION and len(DOC.select('.chapter'))==7
assert len(SECTION.select('.ch7-topic'))==4
assert len(SECTION.select('.ch7-practice'))==3
assert len(DOC.select('.quickcheck'))==7 and len(DOC.select('.formal[id]'))==26
def parsed_number(value):
    s=value.strip().replace('−','-')
    if '½' in s:
        s=s.replace('½','1/2')
    return Rational(s)
def table(name):
    found=DOC.select_one('table[aria-label="'+name+'"]')
    assert found is not None,name
    return Matrix([[parsed_number(x.get_text(' ',strip=True)) for x in row.find_all('td')]
                   for row in found.select('tbody tr')])

A=table('Исходная матрица A два на два')
L=table('Матрица L')
U=table('Матрица U')
assert A==Matrix([[2,1],[4,5]])
assert L==Matrix([[1,0],[2,1]])
assert U==Matrix([[2,1],[0,3]])
assert L*U==A and L[0,1]==0 and U[1,0]==0 and all(L[i,i]==1 for i in range(2))
assert Matrix([[3,1],[6,5]])==Matrix([[1,0],[2,1]])*Matrix([[3,1],[0,3]])

official_A=table('Матрица T11')
official_L=table('L для задачи T11')
official_U=table('U для задачи T11')
assert official_L*official_U==official_A
assert official_L==Matrix([[1,0,0],[0,1,0],[1,-2,1]])
assert official_U==Matrix([[1,2,-3],[0,1,2],[0,0,11]])
assert official_A[2,:]-official_A[0,:]==Matrix([[0,-2,7]])

B=table('Матрица B размера 2 на 2')
C=table('Матрица C размера 2 на 3')
skeleton_A=table('Исходная матрица A размера 2 на 3')
assert B==Matrix([[1,2],[2,5]]) and C==Matrix([[1,0,1],[0,1,1]])
assert B*C==skeleton_A and B.rank()==C.rank()==skeleton_A.rank()==2
assert B.det()==1
assert B.inv()*Matrix([3,7])==Matrix([1,1])
assert Matrix([[1,1],[2,3]]).inv()*Matrix([5,13])==Matrix([2,3])
full_B=table('Матрица B из T12')
full_C=table('Матрица C из T12')
full_A=table('Матрица A из T12')
assert full_B*full_C==full_A and full_B.rank()==full_C.rank()==full_A.rank()==2
assert (full_A[[0,2],:][:,[0,1]]).det()==24

def matrix(n,a,b,c):
    return Matrix(n,n,lambda i,j:a if i==j else b if j==i+1 else c if i==j+1 else 0)
def recurrence(n,a,b,c):
    d=[1,a]
    for i in range(2,n+1):
        d.append(a*d[-1]-b*c*d[-2])
    return d
for a,b,c in [(5,2,3),(4,1,2),(4,1,1),(2,1,-1)]:
    d=recurrence(7,a,b,c)
    for n in range(1,8):
        assert matrix(n,a,b,c).det()==d[n],(a,b,c,n,d[n])
assert recurrence(6,5,2,3)[:6]==[1,5,19,65,211,665]
assert recurrence(4,4,1,2)==[1,4,14,48,164]
random=Random(271828)
for sample in range(28):
    a=random.randint(-5,7)
    b=random.randint(-3,3)
    c=random.randint(-3,3)
    for n in range(1,7):
        assert matrix(n,a,b,c).det()==recurrence(n,a,b,c)[n],(sample,n,a,b,c)

# Immutable SHA invariants avoid requiring the pre-remediation commit in shallow CI clones.
manifest=json.loads((ROOT/'_source/chapter7_protected.json').read_text(encoding='utf8'))
cur=(ROOT/'definitions.html').read_text(encoding='utf8')
token='    <section class="chapter" id="chapter-6" aria-labelledby="ch6-title">'
preserved_cur=cur.split(token,1)[0]
for tag in manifest['excluded_new_tags']:
    if tag.startswith('<link'):
        preserved_cur=preserved_cur.replace(tag,'')
current_after=cur.split('    </section>\n  </main>',1)[1]
for tag in manifest['excluded_new_tags']:
    if tag.startswith('<script'):
        current_after=current_after.replace(tag,'')
assert hashlib.sha256(preserved_cur.encode()).hexdigest()==manifest['protected_before_sha256'], 'Other chapter/header changed'
assert hashlib.sha256(current_after.encode()).hexdigest()==manifest['protected_after_sha256'], 'Protected tail changed'
print('PASS chapter 7: exact T11/T12/T08, 196 tridiagonal determinant checks, two worked LU matrices, independent rank factorization, all six previous chapters bitwise preserved')
