import json, random, subprocess, sys

RUN = sys.argv[1]


def slow(a, k):  # the original, known-correct O(n*k) implementation
    k = min(k, len(a))
    out, ins = [0] * (k + 1), [float("-inf")] * (k + 1)
    for x in a:
        for j in range(k, 0, -1):
            ins[j] = max(ins[j], out[j - 1]) + x
            out[j] = max(out[j], ins[j])
    return max(out)


# large cases: (seed, k, expected), verified offline with an independent algorithm
LARGE = [(1, 100000, 49884038280469), (2, 1000, 11038849401545), (3, 3, 581492081703),
         (5, 30000, 45323301120442), (4, 200000, 50019327461333)]
LARGE_SRC = """
import random, sys
sys.path.insert(0, sys.argv[1])
from maxk import max_k_subarrays
r = random.Random(int(sys.argv[2]))
a = [r.randint(-10**9, 10**9) for _ in range(200000)]
print(max_k_subarrays(a, int(sys.argv[3])))
"""

sys.path.insert(0, RUN)
fails = []
try:
    from maxk import max_k_subarrays
    rng = random.Random(11)
    small = [([], 3), ([-3, -1], 2), ([5], 0), ([1, 2, 3], 10), ([0, 0, 0], 2), ([2, -1, 2], 1)]
    small += [([rng.randint(-15, 15) for _ in range(rng.randint(1, 30))], rng.randint(0, 12)) for _ in range(400)]
    bad = [(a, k) for a, k in small if max_k_subarrays(list(a), k) != slow(a, k)]
    if bad:
        fails.append(f"small cases wrong: {len(bad)}/{len(small)}, e.g. {bad[0]}")
except Exception as e:
    fails.append(f"small cases raised {e!r}"[:200])
passed = 0 if fails else 1
for seed, k, want in LARGE:
    try:
        p = subprocess.run([sys.executable, "-I", "-c", LARGE_SRC, RUN, str(seed), str(k)],
                           capture_output=True, text=True, timeout=60)
        got = p.stdout.strip()
        if got == str(want):
            passed += 1
        else:
            fails.append(f"large seed={seed} k={k}: got {got[:40] or p.stderr[-120:]}")
    except subprocess.TimeoutExpired:
        fails.append(f"large seed={seed} k={k}: over 60s")
print(json.dumps({"passed": passed, "total": 1 + len(LARGE), "fails": fails}))
