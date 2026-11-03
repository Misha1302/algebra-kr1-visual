#!/usr/bin/env python3
"""Independent exact checks for all 25 hand-authored new versions of official exercises."""
from pathlib import Path
import json, itertools
from sympy import Matrix, Rational, symbols, eye, zeros, diag, factor, solve
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'_source/practice_variants.json').read_text(encoding='utf8'))
assert len(data)==25
passed=[]
def ok(id,condition):
    assert condition,id
    assert data[id]['statement'] and data[id]['answer'] and data[id]['reason']
    passed.append(id)
def perm(n,*cycles):
    p=list(range(1,n+1))
    for cyc in cycles:
        for a,b in zip(cyc,cyc[1:]+cyc[:1]):p[a-1]=b
    return tuple(p)
def compose(p,q):return tuple(q[v-1] for v in p) # apply left first
def inverse(p):
    q=[None]*len(p)
    for i,v in enumerate(p):q[v-1]=i+1
    return tuple(q)
def power(p,n):
    result=tuple(range(1,len(p)+1))
    while n:
        if n&1: result=compose(result,p)
        p=compose(p,p);n>>=1
    return result
A=Matrix([[1,1],[0,1]]);B=Matrix([[2,1],[1,0]])
ok('T01',(2*B)**2-(B*A.inv()-eye(2)).T==Matrix([[19,7],[9,6]]))
M=Matrix([[2,1],[1,1]]);b=Matrix([4,3])
ok('T02',M.inv()*b==Matrix([1,2]))
arr=[4,1,2,3,5]
invs=sum(a>b for i,a in enumerate(arr) for b in arr[i+1:])
ok('T03',invs%2==1 and set(arr)==set(range(1,6)))
target=perm(8,(1,2,4),(3,5,6))
sample=perm(8,(1,4,2),(3,6,5))
roots=sum(compose(p,p)==target for p in itertools.permutations(range(1,9)))
ok('T04',roots==8 and compose(sample,sample)==target)
M=Matrix([[2,1],[1,1]]);C=Matrix([[4,3],[6,3]]);X=Matrix([[1,2],[3,0]])
ok('T05',X*M==C and C*M.inv()==X)
A=Matrix([[3,1],[1,3]]);B=Matrix([[1,2],[0,1]])
K=A.T-2*eye(2);R=B.inv()-B.T
ok('T06',K.rank()<K.row_join(R).rank())
x=symbols('x')
D=Matrix([[x,2,1],[1,1,0],[0,3,2]]).det()
ok('T07',D==2*x-1 and D.subs(x,Rational(7,2))==6)
def tri(n,a,b,c):
    return Matrix(n,n,lambda i,j:a if i==j else b if j==i+1 else c if i==j+1 else 0)
ok('T08',tri(2,4,1,2).det()==14 and tri(3,4,1,2).det()==48)
lam=symbols('lam')
A=diag(1,2,lam)
ok('T09',A.det()==2*lam and A.subs(lam,0).rank()==2 and A.subs(lam,3).rank()==3)
x,y=symbols('x y')
A=Matrix([[1,0,1,0],[0,1,0,1],[x,y,2,3]])
minors=[A[:,list(cols)].det() for cols in itertools.combinations(range(4),3)]
ok('T10',solve(minors,(x,y))=={x:2,y:3} and A.subs({x:2,y:3}).rank()==2)
L=Matrix([[1,0,0],[2,1,0],[-1,3,1]]);U=Matrix([[2,1,-1],[0,3,2],[0,0,4]])
ok('T11',L*U==Matrix([[2,1,-1],[4,5,0],[-2,8,11]]))
A=Matrix([[1,2,5],[2,1,4],[3,3,9]])
BB=A[:,0:2];CC=Matrix([[1,0,1],[0,1,2]])
ok('T12',BB*CC==A and BB.rank()==CC.rank()==A.rank()==2)
S=perm(4,(1,3),(2,4))
commuters=[p for p in itertools.permutations(range(1,5)) if compose(p,S)==compose(S,p)]
ok('N184',len(commuters)==8)
results=[]
for n in [4,5]:
    A=diag(*([7]+[1]*(n-1)))
    cols=[A[:,j]+A[:,(j-1)%n] for j in range(n)]
    C=Matrix.hstack(*cols)
    results.append(C.det())
ok('N230',results==[0,14])
A=diag(-5,1,1);J=Matrix([[0,0,1],[0,1,0],[1,0,0]])
ok('N231',(A.T*J).det()==5)
ok('N283',all((3*eye(n)+Matrix.ones(n,n)).det()==3**(n-1)*(n+3) for n in range(1,6)))
ok('N299',tri(4,3,1,1).det()==55)
def special(n):
    A=zeros(n,n)
    for i in range(n):
        A[i,i]=4 if i<2 else 3
        if i<n-1:A[i,i+1]=3 if i==0 else 1
        if i>0:A[i,i-1]=2 if i==1 else 1
    return A
ok('N302',[special(n).det() for n in [2,3,4]]==[10,26,68])
xs=[0,2];A=Matrix([[1+t,1+t*t] for t in xs])
ok('N348',A.det()==2)
ok('N365',tri(4,2,1,-1).det()==29)
J=Matrix.ones(3,3);A=2*(J-eye(3));inv=-eye(3)/2+J/4
ok('N853',A*inv==eye(3) and inv*A==eye(3))
S=perm(6,(1,2,3),(4,5))
ok('N177',power(S,152)==perm(6,(1,3,2)))
A=perm(3,(1,2));B=perm(3,(2,3));C=perm(3,(1,2,3))
X=compose(compose(inverse(A),C),inverse(B))
ok('N178',X==C and compose(compose(A,X),B)==C)
t=symbols('t');f=t**3-2*t+1
ok('N586',[f.subs(t,k) for k in [-1,0,1,2]]==[2,1,0,5])
A=Matrix([[1,2],[3,4]])
ok('N829',A*A-5*A-2*eye(2)==zeros(2,2))
print('PASS',len(passed),'new official-style variants independently checked:',','.join(passed))
