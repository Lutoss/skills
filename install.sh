#!/usr/bin/env bash
# Install a skill pack (claude or codex) globally or into a project.
set -eu

usage() {
  cat <<'EOF'
Usage: install.sh <pack> [scope] [target-dir]

  pack        claude | codex
  scope       global (default) | project
  target-dir  project scope only: target directory (default: current dir)

Destinations:
  claude global    $HOME/.claude/skills
  claude project   <target-dir>/.claude/skills
  codex  global    $HOME/.agents/skills
  codex  project   <target-dir>/.agents/skills

Examples:
  ./install.sh claude
  ./install.sh codex project /path/to/repo
EOF
}

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  usage
  exit 0
fi

REPO_DIR=$(cd "$(dirname "$0")" && pwd)
PACK="${1:-}"
SCOPE="${2:-global}"
TARGET="${3:-.}"

case "$PACK" in
  claude) SUBDIR=".claude/skills" ;;
  codex)  SUBDIR=".agents/skills" ;;
  *)
    echo "Error: pack must be 'claude' or 'codex'." >&2
    echo "" >&2
    usage >&2
    exit 1
    ;;
esac

case "$SCOPE" in
  global)
    DEST="$HOME/$SUBDIR"
    ;;
  project)
    if [ ! -d "$TARGET" ]; then
      echo "Error: target directory '$TARGET' does not exist." >&2
      exit 1
    fi
    DEST="$(cd "$TARGET" && pwd)/$SUBDIR"
    ;;
  *)
    echo "Error: scope must be 'global' or 'project'." >&2
    echo "" >&2
    usage >&2
    exit 1
    ;;
esac

mkdir -p "$DEST"

installed=0
overwritten=0
names=""

for group in MattSkills LutossSkills; do
  GROUP_DIR="$REPO_DIR/$PACK/$group"
  if [ ! -d "$GROUP_DIR" ]; then
    echo "Warning: group folder '$GROUP_DIR' not found, skipping." >&2
    continue
  fi
  for skill in "$GROUP_DIR"/*; do
    [ -d "$skill" ] || continue   # skip loose files (LICENSE, README, ...)
    name=$(basename "$skill")
    if [ -d "$DEST/$name" ]; then
      echo "Overwriting existing skill: $name"
      rm -rf "$DEST/${name:?}"
      overwritten=$((overwritten + 1))
    fi
    cp -R "$skill" "$DEST/"
    names="$names $name"
    installed=$((installed + 1))
  done
done

echo ""
echo "Installed $installed skill(s) to $DEST ($overwritten overwritten):"
for n in $names; do
  echo "  - $n"
done
echo ""
echo "First step after install: run setup-matt-pocock-skills once in your target repo."
echo "Then use ask-matt as the router to find the right skill."
