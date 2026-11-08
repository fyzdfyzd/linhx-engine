"""python -I test_tqa.py — kiểm các thước đo cơ bản của tqa.py."""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import tqa

T = "# Title\n\nCertainly! This is not just a test but a promise. It works — really. It works, again.\n\n- one\n- two"
assert tqa.tach_cau(T)[0].startswith('Certainly'), tqa.tach_cau(T)
assert tqa.do(T, {'kind': 'regex', 'pattern': r'^certainly', 'flags': 'i', 'scope': 'first_sentence', 'unit': 'presence'}) == 1.0
assert tqa.do(T, {'kind': 'regex', 'pattern': r'\bnot just\b[^.]*\bbut\b', 'unit': 'count'}) == 1.0
assert tqa.do(T, {'kind': 'regex', 'pattern': r'^it\b', 'flags': 'i', 'scope': 'sentence_start', 'unit': 'count'}) == 2.0
assert abs(tqa.do(T, {'kind': 'stat', 'name': 'bullet_share'}) - 2 / 4) < 1e-9
assert tqa.do(T, {'kind': 'stat', 'name': 'opener_repeat'}) > 0
assert tqa.do("Không chỉ đẹp mà còn rẻ. Trong bối cảnh đó, ta đi.", {'kind': 'regex', 'pattern': 'không chỉ[^.]*mà còn', 'flags': 'i', 'unit': 'count'}) == 1.0
rng = random.Random(0)
a = [rng.gauss(3, 1) for _ in range(200)]; b = [rng.gauss(1, 1) for _ in range(800)]
r, lo, hi, p = tqa.so_sanh(a, b, 'higher')
assert 2.5 < r < 3.5 and lo > 2 and p < 1e-6, (r, lo, hi, p)
r, lo, hi, p = tqa.so_sanh(a[:30], a[30:60], 'higher', boot=500)
assert lo < 1 < hi and p > .05, (lo, hi, p)
assert tqa.holm([0.01, 0.04, 0.03]) == [0.03, 0.06, 0.06]
print('7/7 + thống kê: ĐẠT')
