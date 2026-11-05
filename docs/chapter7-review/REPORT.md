# Chapter 7 — pedagogical rewrite and verification

**Baseline:** commit b0d921799e817a10ae63b94666d2583c9c1acbc5 (published version before this change).
**Scope:** Chapter 7 in definitions.html, scoped CSS/JS, reproducible source, tests, documentation and screenshots.
**Content preservation:** immutable hashes for the previous six chapters and protected document tail in _source/chapter7_protected.json.

## Problem and repair

Previously the lesson moved from A=LU to a finished matrix with too little explanation of why the multiplier in L was 2 (or −2), how the coefficients in C were solved, and why a determinant recurrence contains −bc. The learner could check a result but not necessarily reproduce the method.

The replacement has three independent guided explanations:

1. **LU (T11).** Define triangular matrices, compute k=4/2 in 2×2, execute R₂←R₂−2R₁ for every element, record the multiplier in L, verify LU=A, then work the exact official 3×3 example. Include a counterexample explaining PA=LU and pivoting.
2. **Rank/skeleton (T12).** Identify two independent original columns with a nonzero minor, solve two equations for the third column, construct C column-by-column, show dimensions and official 4×3 factorization.
3. **Three-diagonal determinant (T08).** Define D₀ and D₁, directly compute D₂, expand D₃ by the first row, explain the negative cofactor and bc, use the recurrence for orders 2–6 and two parameter sets.

Each includes a numerical check with actionable feedback, an optional revealed solution, and a link to official problems. The chapter-level navigation jumps directly to each part. The numerical exercises do not mark learning as mastered.

## Verification results (local branch)

| Evidence | Result and limitation |
| --- | --- |
| tests/chapter7_math_oracle.py | PASS: independent exact SymPy verification of LU in 2×2 and 3×3, B·C and ranks in 2×3 and 4×3, plus 196 three-diagonal determinant cases. |
| tests/chapter7_e2e.py | PASS: LU previous/next/reset, keyboard Enter, column selection, recurrence variants, invalid/partial/correct answers and progress noninterference. |
| Responsive | PASS at 320, 360, 390, 768, 1366 and 1920 px without document-level horizontal overflow. |
| tests/accessibility_wcag.py | PASS: axe-core 4.10.3 checks of 17 route/viewport combinations (WCAG 2.0/2.1 A/AA automated rules). Not a manual screen-reader audit. |
| Historic and remediation tests | PASS: all previous suites, including 297 internal links. |
| Real local HTTP | PASS: 34 files (including PDF), 23 browser checks, SHA agreement with the local checkout. |
| Visual inspection | Actual screenshots captured and inspected on desktop and mobile; compare the attached before/after captures. |

**Build contract:** _source/build_chapter7.py replaces exactly one bounded region in definitions.html from _source/chapter7_content.html. CI regenerates it and rejects source/output drift. The earlier six chapters and the document tail are mechanically protected against unintended changes.

## Evidence

- before_1366.png and before_390.png: original baseline Chapter 7, captured from the original Git revision with matching assets.
- after_chapter7_top_1366.png and after_lu_1366.png: new introduction and first lesson.
- after_skeleton_1366.png and after_recurrence_1366.png: other lessons.
- after_lu_390.png, after_skeleton_390.png and after_recurrence_390.png: phone layout.
- acceptance.json: checked widths, screenshot index and E2E state.

## Limits and open human acceptance

- No real-student controlled experiment has taken place. Browser checks and mathematical oracles cannot prove that every beginner will understand.
- The numerical checker verifies arithmetic, not unrestricted handwritten proofs. A student must compare their full derivation with the provided explanation.
- Exercises are chosen finite variants, not an unlimited task generator.
- Printable legacy PDFs are not modified; the improved material is online at definitions.html#chapter-6.
- External source reuse and permissions remain as described in docs/remediation/CONTENT_PROVENANCE.md.

**Release criterion:** merge only after green GitHub CI; separately verify the real public GitHub Pages HTML/CSS/JS and the new Chapter 7 interactions.
