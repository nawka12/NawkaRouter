"""A small backtracking regular-expression engine.

search(pattern, text) must behave exactly like Python's re.search(pattern, text)
for the syntax below, returning (m.span(), m.groups()) on a match and None
otherwise. Do not use the re module (or sre_parse / sre_compile / _sre).

Supported syntax:
- literal characters and `.` (any character except "\\n")
- escapes \\d \\D \\w \\W \\s \\S, and a backslash before a punctuation character
  for that literal character (e.g. \\. \\* \\( \\\\ \\-)
- character classes: [abc], ranges [a-z0-9_], negation [^...], and the
  escapes above inside classes (including \\] \\\\ \\-)
- anchors ^ and $ (no flags: $ matches at the end, or just before a final "\\n")
- groups: capturing (...), non-capturing (?:...), alternation |
- quantifiers *, +, ?, {m}, {m,}, {m,n}, and their lazy forms *?, +?, ??, {m}?, {m,}?, {m,n}?
- backreferences \\1 through \\9

Invalid patterns (anything Python's re.compile rejects among this syntax) raise ValueError.
"""


def search(pattern: str, text: str):
    raise NotImplementedError
