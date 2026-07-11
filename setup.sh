#!/usr/bin/env bash
#
# Symlinks this repo's config files into their expected locations.
# Safe to re-run: existing real files/dirs are backed up with a .bak suffix
# before the symlink is created, and existing correct symlinks are skipped.

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# "source (relative to this repo):target (absolute path)" pairs
LINKS=(
  "nvim:$HOME/.config/nvim"
  "tmux.conf:$HOME/.tmux.conf"
  "wezterm:$HOME/.config/wezterm"
  "zshrc:$HOME/.zshrc"
  "skills:$HOME/.copilot/skills"
  # Shared agent guidelines. One source file, linked to each tool's global path:
  #   Claude Code       -> ~/.claude/CLAUDE.md
  #   Codex CLI         -> ~/.codex/AGENTS.md
  #   GitHub Copilot CLI-> ~/.copilot/copilot-instructions.md
  "AGENTS.md:$HOME/.claude/CLAUDE.md"
  "AGENTS.md:$HOME/.codex/AGENTS.md"
  "AGENTS.md:$HOME/.copilot/copilot-instructions.md"
)

for pair in "${LINKS[@]}"; do
  src="$DOTFILES_DIR/${pair%%:*}"
  target="${pair##*:}"

  if [ -L "$target" ] && [ "$(readlink "$target")" = "$src" ]; then
    echo "OK      $target already linked"
    continue
  fi

  mkdir -p "$(dirname "$target")"

  if [ -e "$target" ] || [ -L "$target" ]; then
    backup="${target}.bak"
    echo "BACKUP  $target -> $backup"
    mv "$target" "$backup"
  fi

  ln -s "$src" "$target"
  echo "LINKED  $target -> $src"
done

echo "Done."
