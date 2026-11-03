#!/usr/bin/env python3
"""Independent SymPy oracle for every published seed of transfer practice.

Reads content data but recomputes results by a separate mathematical method:
matrix operations, rank, exact Gauss, recurrence, factorization. No JS oracle reuse.
"""
import json
from pathlib import Path
from sympy import Matrix, Rational, eye, zeros
ROOT=Path(__file__).resolve().parents[1]
bank=json.loads((ROOT/'_source/transfer_cases.json').read_text(encoding='utf8'))
all_cases={c['id']:c for items in bank.values() for c in items}
assert len(bank)==8 and len(all_cases)==24
checked=0
def answer(case_id,field,expected):
    global checked
    c=all_cases[case_id]
    f=next(x for x in c['fields'] if x['id']==field)
    got=f['answer']
    if isinstance(expected,str):
        assert got==expected,(case_id,field,got,expected)
    else:
        assert Rational(got)==Rational(expected),(case_id,field,got,expected)
    checked+=1
def mat(case_id,key='A'):return Matrix(all_cases[case_id]['visual'][key])
# Independent exact permutation oracle, with the course left-to-right convention.
def perm(n,*cycles):
    out=list(range(1,n+1))
    for cycle in cycles:
        for a,b in zip(cycle,cycle[1:]+cycle[:1]):out[a-1]=b
    return tuple(out)
def mulL(p,q):return tuple(q[v-1] for v in p)
def inverse(p):
    out=[None]*len(p)
    for i,v in enumerate(p):out[v-1]=i+1
    return tuple(out)
s1=perm(3,(1,2,3));t1=perm(3,(1,2))
answer('PRA1','left',mulL(s1,t1)[0]);answer('PRA1','right',mulL(t1,s1)[0]);answer('PRA1','power',mulL(s1,s1)[0])
s2=perm(4,(1,2),(3,4));t2=perm(4,(1,2,3,4))
answer('PRA2','left',mulL(s2,t2)[0]);answer('PRA2','right',mulL(t2,s2)[0]);answer('PRA2','power',mulL(s2,s2)[2])
a=perm(3,(1,2));b=perm(3,(2,3));c=perm(3,(1,2,3))
x=mulL(mulL(inverse(a),c),inverse(b))
assert mulL(mulL(a,x),b)==c
for idx,v in enumerate(x):answer('PRA3','x'+str(idx+1),v)

for case_id,r,c in [('M1',0,1),('M2',1,0)]:
    a,b=mat(case_id),mat(case_id,'B')
    p=a*b
    answer(case_id,'first',a[r,0]*b[0,c])
    answer(case_id,'result',p[r,c])
answer('M2','transpose','3,2')
assert mat('M3').cols != mat('M3','B').rows
answer('M3','possible','no')

for id, a, b, operation in [
 ('G1',Matrix([[1,1],[2,-1]]),Matrix([5,1]),-2),
 ('G2',Matrix([[1,-2],[-2,5]]),Matrix([3,-7]),2),
]:
    x=a.inv()*b
    answer(id,'rhs',b[1]+operation*b[0])
    answer(id,'x',x[0]); answer(id,'y',x[1])
assert Matrix([[0,2],[1,1]]).det()!=0
g3=Matrix([[0,2],[1,1]]).inv()*Matrix([4,5])
answer('G3','pivot','swap');answer('G3','x',g3[0]);answer('G3','y',g3[1])
for id in ['D1','D2','D3']:
    A=mat(id)
    answer(id,'main',A[0,0]*A[1,1])
    answer(id,'off',A[0,1]*A[1,0])
    answer(id,'det',A.det())
for id in ['I1','I2','I3']:
    A=mat(id)
    answer(id,'det',A.det())
    if A.det():
        answer(id,'entry',A.inv()[0,1])
    else:
        answer(id,'exists','no')
for id in ['R1','R2','R3']:
    A=mat(id)
    answer(id,'minor',A[:,0:2].det())
    answer(id,'rank',A.rank())
for id,b in [('S1',[4,2]),('S2',[4,8]),('S3',[4,9])]:
    A=Matrix([[1,1],[1,-1]]) if id=='S1' else Matrix([[1,1],[2,2]])
    augmented=A.row_join(Matrix(b))
    ra,rb=A.rank(),augmented.rank()
    classification='none' if ra!=rb else 'one' if ra==A.cols else 'many'
    answer(id,'rankA',ra);answer(id,'rankAug',rb);answer(id,'type',classification)
A=mat('A1');l=A[1,0]/A[0,0];u22=A[1,1]-l*A[0,1]
L=Matrix([[1,0],[l,1]]);U=Matrix([[A[0,0],A[0,1]],[0,u22]])
assert L*U==A
answer('A1','l21',l);answer('A1','u22',u22)
A=mat('A2');C=A[:,0:2];v=C.inv()*A[:,2]
assert C*Matrix(v)==A[:,2]
answer('A2','rank',A.rank());answer('A2','c1',v[0]);answer('A2','c2',v[1])
D=[1,4]
for n in range(2,5):
    D.append(4*D[-1]-D[-2])
    A=Matrix(n,n,lambda i,j: 4 if i==j else 1 if abs(i-j)==1 else 0)
    assert A.det()==D[n],(n,A.det(),D[n])
for i in range(2,5):answer('A3',f'd{i}',D[i])
print(f'PASS: {len(all_cases)} independent seed oracles; {checked} exact-field checks, including 2/7, zeros and rank; left-to-right permutations covered by tests/math_invariants.py')
