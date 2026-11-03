#!/usr/bin/env python3
"""Independent arithmetic checks for site examples and left-to-right conventions."""
from itertools import permutations
from sympy import Matrix
A=Matrix([[1,2,3],[0,4,5],[1,0,6]])
assert A.det()==22
assert Matrix([[2,1],[3,4]]).det()==5
assert Matrix([[3,4],[2,1]]).det()==-5
assert Matrix([[4,2],[3,4]]).det()==10
assert Matrix([[2,1],[9,7]]).det()==5
for axis in range(3):
    row_sum=sum(A[axis,j]*(-1)**(axis+j)*A.minor_submatrix(axis,j).det() for j in range(3))
    col_sum=sum(A[i,axis]*(-1)**(i+axis)*A.minor_submatrix(i,axis).det() for i in range(3))
    assert row_sum==col_sum==A.det()
for n in range(1,8):
    a,b,c=5,2,3
    t=Matrix(n,n,lambda i,j:a if i==j else b if j==i+1 else c if i==j+1 else 0)
    assert t.det()==3**(n+1)-2**(n+1)
def mul_left(x,y):return tuple(y[x[i]-1] for i in range(len(x)))
def inv(x):
    y=[0]*len(x)
    for i,a in enumerate(x):y[a-1]=i+1
    return tuple(y)
aa=(7,3,2,1,6,5,4);bb=(3,1,2,7,4,5,6);cc=(5,1,3,6,4,7,2)
xx=mul_left(mul_left(inv(aa),cc),inv(bb))
assert xx==(7,1,2,3,4,5,6)
assert mul_left(mul_left(aa,xx),bb)==cc
sigma=(2,1,3);tau=(1,3,2)
assert mul_left(sigma,tau)==(3,1,2)
assert mul_left(tau,sigma)==(2,3,1)
target=(2,3,1,5,6,4,7,8)
roots=[p for p in permutations(range(1,9)) if mul_left(p,p)==target]
assert len(roots)==8
print('PASS: det2, det3 six expansions, row operation effects, tridiagonal n=1..7, left composition, task 178 all 7, T04 all 8 roots')
