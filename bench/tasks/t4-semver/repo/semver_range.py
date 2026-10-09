"""npm-compatible semver range matching.

Implement satisfies(version, range_) so it returns exactly what
node-semver's `satisfies(version, range)` returns with default options
(no loose mode, no includePrerelease). Versions are strict semver:
1.2.3, 1.2.3-beta.1, 1.2.3+build.5, 1.2.3-rc.1+build.5.

Range syntax to support (https://github.com/npm/node-semver#ranges):
- primitive comparators: <, <=, >, >=, = (or no operator), with full or
  partial versions (e.g. >1, <=1.2, =1.2)
- comparator sets: comparators separated by whitespace, all must match;
  sets are joined by || and any set may match
- hyphen ranges: 1.2.3 - 2.3.4, with partial versions on either side
- X-ranges: *, x, X, 1.x, 1.2.*, and the empty string
- tilde ranges: ~1.2.3, ~1.2, ~1, ~0.2.3, ~1.2.3-beta.2
- caret ranges: ^1.2.3, ^0.2.3, ^0.0.3, ^1.2.x, ^0.0.x, ^0.x, ^0.0, ^1.2.3-beta.2
- prerelease tags: a version that has a prerelease tag only satisfies a
  comparator set if at least one comparator in that set has the same
  major.minor.patch and also has a prerelease tag. Prerelease precedence
  follows the SemVer 2.0.0 spec, section 11.
- build metadata (+...) is ignored for matching.

An invalid version or an invalid range returns False (never raises).
"""


def satisfies(version: str, range_: str) -> bool:
    raise NotImplementedError
