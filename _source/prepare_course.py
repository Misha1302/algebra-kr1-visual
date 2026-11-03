from pathlib import Path
import zipfile,re
root=Path('/home/micodiy/razakov/sites/algebra-kr1-visual')
out=root/'_source'
out.mkdir(exist_ok=True)
with zipfile.ZipFile('/home/micodiy/Downloads/Algebra_KR1_2026_CORRECTED_PACKAGE.zip') as z:
 s=z.read('Algebra_KR1_2026_FIXED/01_COURSE/Algebra_KR1_2026_CORRECTED.md').decode('utf-8')
def fix(old,new,quantity=1):
 global s
 assert s.count(old)==quantity,(old,s.count(old))
 s=s.replace(old,new)
fix(r'$(\sigma\tau)(i)=\sigma(\tau(i))$, то есть при такой договорённости **сначала действует правая**.',
    r'$(\sigma\tau)(i)=\tau(\sigma(i))$, то есть **сначала действует левая** подстановка, затем правая. Например, $(1\,2)(2\,3)=(1\,3\,2)$.')
fix(r'композиция слева с транспозицией меняет чётность: $\operatorname{sgn}(\pi\circ\sigma)=-\operatorname{sgn}\sigma$.',
    r'композиция с транспозицией меняет чётность. В нашем соглашении (сначала левый множитель) $\sigma\pi$ означает сначала $\sigma$, затем $\pi$, и $\operatorname{sgn}(\sigma\pi)=-\operatorname{sgn}\sigma$.')
fix(r'Сделаем замену $\rho=\pi\circ\sigma$.',r'Сделаем замену $\rho=\sigma\pi$ (сначала $\sigma$, затем $\pi$).')
fix(r'замена индекса $\rho=\pi\sigma$',r'замена индекса $\rho=\sigma\pi$')
fix(r'С композиционным соглашением $(AB)(i)=A(B(i))$ решение обязано быть',
    r'При соглашении **сначала левая** подстановка: $(AB)(i)=B(A(i))$. Решение равенства в группе:')
fix(r'для каждого $i$ применить $B^{-1}$, затем $C$, затем $A^{-1}$. Например, $B^{-1}(1)=2$, $C(2)=1$, $A^{-1}(1)=4$, значит $X(1)=4$.',
    r'для каждого $i$ применить $A^{-1}$, затем $C$, затем $B^{-1}$. Например, $A^{-1}(1)=4$, $C(4)=6$, $B^{-1}(6)=7$, значит $X(1)=7$.')
fix(r'\\4&2&6&7&1&3&5\end{pmatrix}=(1\,4\,7\,5)(3\,6)',
    r'\\7&1&2&3&4&5&6\end{pmatrix}=(1\,7\,6\,5\,4\,3\,2)')
fix(r'$(AXB)(1)=A(X(B(1)))=A(X(3))=A(6)=5=C(1)$',
    r'$(AXB)(1)=B(X(A(1)))=B(X(7))=B(6)=5=C(1)$')
fix('**Внимание:** порядок композиции подстановок иногда определяют иначе. Если преподаватель принял «сначала левую», необходимо следовать **его** соглашению и корректно переписать все формулы; здесь использована и явно объявлена стандартная для функций композиция «сначала правая».',
    '**Соглашение курса:** произведения подстановок выполняем слева направо. В других источниках порядок может быть обратным; не смешивайте соглашения.')
fix('# 3. Перестановки и подстановки (D05–D07, T03–T04)',
    '# 3. Перестановки и подстановки (D05–D07, T03–T04)\n\n> **Соглашение курса:** подстановки перемножаем слева направо: $(\\sigma\\tau)(i)=\\tau(\\sigma(i))$. Сначала действует $\\sigma$, затем $\\tau$. Для матричного произведения действует обычное правило строк и столбцов.')
expected=['D%02d'%i for i in range(1,27)]+['P%02d'%i for i in range(1,12)]+['T%02d'%i for i in range(1,13)]+['N'+str(i) for i in [184,230,231,283,299,302,348,365,853,177,178,586,829]]
lines=[];in_defs=False;found=[]
for line in s.splitlines(keepends=True):
 if line.startswith('# 9. Все 26'):in_defs=True
 if line.startswith('# 10. Все 11'):in_defs=False
 m=re.match(r'^\*\*(D\d\d)\.',line) if in_defs else None
 if not m:m=re.match(r'^## (P\d\d|T\d\d|№\d+)\.',line)
 if m:
  id=m.group(1).replace('№','N')
  found.append(id);lines.append('<a id="'+id+'"></a>\n\n')
 lines.append(line)
assert set(expected)==set(found),(set(expected)-set(found),set(found)-set(expected))
s=''.join(lines)
p=out/'Algebra_KR1_2026_SITE_CONVENTION.md';p.write_text(s)
(out/'README.md').write_text('Online source uses course-specific left-to-right permutation convention; older visual PDF contains conflicting right-to-left examples.\n')
print('CREATED',p,'anchors',len(found),'bytes',p.stat().st_size)
