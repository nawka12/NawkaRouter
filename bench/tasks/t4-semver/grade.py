import json, pathlib, sys

sys.path.insert(0, sys.argv[1])
from semver_range import satisfies  # noqa: E402

cases = json.loads((pathlib.Path(__file__).parent / "cases.json").read_text())
fails = []
for v, r, want in cases:
    try:
        got = satisfies(v, r)
    except Exception as e:  # spec says never raise
        got = f"raised {type(e).__name__}"
    if got is not want:
        fails.append(f"{v} | {r!r} -> {got}, want {want}")
print(json.dumps({"passed": len(cases) - len(fails), "total": len(cases), "fails": fails[:15]}))
