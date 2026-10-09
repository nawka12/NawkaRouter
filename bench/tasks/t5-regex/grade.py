import json, pathlib, re, signal, sys

CASES = [
    ("abc", "xxabcxx"), ("a.c", "abc"), ("a.c", "a\nc"), ("^abc", "abcabc"), ("abc$", "abcabc"),
    ("abc$", "abc\n"), ("^$", ""), ("x*", "aaa"), ("a+", "baaab"), ("ba?b", "bb"), ("a{2}", "aaaa"),
    ("a{2,}", "aaaaa"), ("a{2,3}", "aaaaa"), ("a{2,3}?", "aaaa"), ("a{2}?", "aaa"), ("a{2,}?", "aaaa"),
    ("a*?b", "aaab"), ("<.*>", "<a><b>"), ("<.*?>", "<a><b>"), ("a??b", "ab"), ("a+?", "aaa"),
    ("[abc]+", "xxbcaz"), ("[a-c0-2]+", "zz2b1y"), ("[^a-z]+", "abc123def"), (r"[\d\s]+", "ab 12 3x"),
    (r"[\]x]+", "a]x]b"), (r"[a\-z]+", "b-az"), (r"[\\]", "a\\b"), (r"\d+", "abc 123"), (r"\D+", "123abc4"),
    (r"\w+", "!! foo_bar1 ??"), (r"\W+", "ab!?cd"), (r"\s+", "a \t\nb"), (r"\S+", "  xy  "), (r"\.", "a.b"),
    (r"\*\+", "a*+b"), ("[.]", "a.b"), (r"a\-b", "a-b"), (r"\(\)", "f()"), ("a|b|c", "xxc"), ("ab|cd", "xcdab"),
    ("(a|ab)(c|bcd)(d*)", "abcd"), ("(a)(b)?", "ac"), ("(a(b)?)+", "aba"), ("(?:ab)+", "ababa"),
    ("(a|b)*", "abba"), ("(a|b)*c", "abbac"), (r"(\w+)\s(\w+)", "hello world"), ("(a*)*", "b"),
    ("(a*)+", "b"), ("(a|)+b", "aab"), ("(a*)*b", "aaab"), (r"(a+)\1", "aaaa"), (r"(\w)\1", "abccd"),
    (r"(a)?b\1", "b"), (r"(\w+) \1", "hello hello world"), (r"<(\w+)>.*?</\1>", "<a><b>x</b></a>"),
    ("^ab|cd$", "xxcd"), ("a(b|c)*d", "abcbd"), ("(a+?)(a*)", "aaa"), ("(a+)(a+)", "aaaa"),
    ("a$", "a\n"), ("a$\n", "a\n"), ("$", "abc"), ("^", "abc"), (".+", "ab\ncd"), ("(ab){2}", "abababab"),
    ("(ab){2,}?", "ababab"), ("(a|ab)*c", "abac"), ("(x+x+)+y", "xxxxxxxxxxy"), ("a.*b.*c", "axxbyyczz"),
    ("", "abc"), (r"\w+", "café!"), ("(?:(a)|b)*", "ab"), ("(?:a|(b))+", "ab"), ("((a)|b)+", "ab"),
    ("(a)|(b)", "b"), ("x(a|b)?y", "xy"), ("[^\n]+", "ab\ncd"), ("a{0}b", "ab"), ("(a{0,1})*", "aa"),
    ("[a-]+", "a-a"), ("[-a]+", "-a-"), ("[]a]", ""),
    ("(", ""), ("a)", ""), ("[a", ""), ("*a", ""), ("a**", ""), (r"\1", ""), ("a{2,1}", ""),
    ("(?:", ""), ("a|*", ""), ("(a))", ""),
]


def expected(p, t):
    try:
        m = re.search(p, t)
    except re.error:
        return "ValueError"
    return None if m is None else [list(m.span()), list(m.groups())]


want = [expected(p, t) for p, t in CASES]
src = pathlib.Path(sys.argv[1], "minire.py").read_text()
if re.search(r"\bimport\s+(re|sre\w*|_sre)\b|\bfrom\s+(re|sre\w*|_sre)\s+import|__import__|importlib", src):
    print(json.dumps({"passed": 0, "total": len(CASES), "fails": ["uses the re module"]}))
    sys.exit()
sys.path.insert(0, sys.argv[1])
from minire import search  # noqa: E402


def on_alarm(*_):
    raise TimeoutError


signal.signal(signal.SIGALRM, on_alarm)
fails = []
for (p, t), w in zip(CASES, want):
    signal.alarm(2)
    try:
        r = search(p, t)
        got = None if r is None else [list(r[0]), list(r[1])]
    except ValueError:
        got = "ValueError"
    except Exception as e:
        got = f"raised {type(e).__name__}"
    finally:
        signal.alarm(0)
    if got != w:
        fails.append(f"{p!r} on {t!r}: got {got}, want {w}")
print(json.dumps({"passed": len(CASES) - len(fails), "total": len(CASES), "fails": fails[:15]}))
