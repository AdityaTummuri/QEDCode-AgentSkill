#!/usr/bin/env bash
# Build dist/qedcode-skill-<version>.zip: just the skill folder (SKILL.md, references/, examples/).
# Usage: scripts/package.sh [version]   (default: the latest version in CHANGELOG.md)
set -euo pipefail
cd "$(dirname "$0")/.."
version="${1:-$(grep -m1 -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | tr -d '#[] ')}"
[ -n "$version" ] || { echo "No version given and none found in CHANGELOG.md" >&2; exit 1; }
python3 tests/validate_skill.py ${QED:+--qed "$QED"}
mkdir -p dist
out="dist/qedcode-skill-${version}.zip"
rm -f "$out"
(cd skills && zip -qr -X "../$out" qedcode -x '*.DS_Store')
echo "Built $out"
unzip -l "$out"
