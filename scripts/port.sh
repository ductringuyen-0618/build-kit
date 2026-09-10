#!/bin/sh
# Copy one or all skills into a target project in the layout a tool expects.
#   sh scripts/port.sh <skill|all> claude|cursor <target-dir>
# claude: copies skills/<name>/ to <target>/.claude/skills/<name>/
# cursor: writes <target>/.cursor/rules/<name>.mdc from SKILL.md and copies
#         references/, scripts/, examples/, features/ to .cursor/rules/<name>/
set -eu

usage() { echo "usage: $0 <skill|all> claude|cursor <target-dir>" >&2; exit 1; }
[ $# -eq 3 ] || usage
SKILL=$1; TOOL=$2; TARGET=$3
KIT=$(cd "$(dirname "$0")/.." && pwd)
case "$TOOL" in claude|cursor) ;; *) usage ;; esac
mkdir -p "$TARGET"
TARGET=$(cd "$TARGET" && pwd)

# Print the description from SKILL.md frontmatter (handles folded >- values).
description() {
  awk '
    /^---$/ { fm++; next }
    fm == 1 && /^description:/ {
      v = $0; sub(/^description:[ \t]*/, "", v)
      if (v == ">-" || v == ">" || v == "|" || v == "") { folded = 1; next }
      print v; exit
    }
    fm == 1 && folded && /^[ \t]/ { s = $0; sub(/^[ \t]+/, "", s); out = out (out == "" ? "" : " ") s; next }
    fm == 1 && folded { print out; exit }
    fm >= 2 { if (folded) print out; exit }
  ' "$1"
}

# Print everything after the frontmatter.
body() { awk 'fm >= 2 { print; next } /^---$/ { fm++ }' "$1"; }

port_one() {
  name=$1; src="$KIT/skills/$name"
  [ -f "$src/SKILL.md" ] || { echo "no such skill: $name" >&2; exit 1; }
  case "$TOOL" in
    claude)
      dest="$TARGET/.claude/skills/$name"
      rm -rf "$dest"; mkdir -p "$TARGET/.claude/skills"; cp -R "$src" "$dest"
      echo "claude  $dest" ;;
    cursor)
      mkdir -p "$TARGET/.cursor/rules"
      out="$TARGET/.cursor/rules/$name.mdc"
      desc=$(description "$src/SKILL.md" | sed 's/"/\\"/g')
      {
        printf -- '---\ndescription: "%s"\nglobs:\nalwaysApply: false\n---\n' "$desc"
        body "$src/SKILL.md"
      } > "$out"
      for d in references scripts examples features; do
        if [ -d "$src/$d" ]; then
          mkdir -p "$TARGET/.cursor/rules/$name"
          rm -rf "$TARGET/.cursor/rules/$name/$d"
          cp -R "$src/$d" "$TARGET/.cursor/rules/$name/$d"
        fi
      done
      echo "cursor  $out" ;;
  esac
}

if [ "$SKILL" = all ]; then
  for d in "$KIT"/skills/*/; do port_one "$(basename "$d")"; done
else
  port_one "$SKILL"
fi
