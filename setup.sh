#!/usr/bin/env bash
#
# Bootstraps a fresh macOS machine:
#   1. Installs Xcode Command Line Tools (git + C compiler for treesitter).
#   2. Installs Homebrew and the tools in ./Brewfile.
#   3. Installs a default node (LTS) via nvm and the GitHub Copilot CLI.
#   4. Symlinks this repo's config files into their expected locations.
#
# Safe to re-run: every phase is guarded, and existing real files/dirs are
# backed up with a .bak suffix before a symlink is created.

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# 1. Xcode Command Line Tools (provides git and a C compiler for treesitter)
# ---------------------------------------------------------------------------
if xcode-select -p >/dev/null 2>&1; then
  echo "OK      Xcode Command Line Tools already installed"
else
  echo "INSTALL Xcode Command Line Tools"
  xcode-select --install
  echo "        Finish the CLT installer dialog, then re-run this script."
  exit 1
fi

# ---------------------------------------------------------------------------
# 2. Homebrew + Brewfile
# ---------------------------------------------------------------------------
if ! command -v brew >/dev/null 2>&1; then
  echo "INSTALL Homebrew"
  NONINTERACTIVE=1 /bin/bash -c \
    "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Load brew into this shell, handling both Apple Silicon and Intel prefixes.
if [ -x /opt/homebrew/bin/brew ]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
elif [ -x /usr/local/bin/brew ]; then
  eval "$(/usr/local/bin/brew shellenv)"
else
  echo "ERROR   brew not found on PATH after install" >&2
  exit 1
fi

echo "BUNDLE  installing tools from Brewfile"
brew bundle --file="$DOTFILES_DIR/Brewfile"

# ---------------------------------------------------------------------------
# 3. node (via nvm) + GitHub Copilot CLI
# ---------------------------------------------------------------------------
export NVM_DIR="$HOME/.nvm"
mkdir -p "$NVM_DIR"
# shellcheck disable=SC1091
if [ -s "$(brew --prefix nvm)/nvm.sh" ]; then
  # nvm.sh is not safe under `set -euo pipefail` -- it sources/uses unbound
  # internal variables, which `set -u` treats as a fatal error that kills the
  # whole script. Relax errexit/nounset while we drive nvm, then restore.
  set +eu
  \. "$(brew --prefix nvm)/nvm.sh"

  if [ "$(nvm version node)" = "N/A" ]; then
    echo "INSTALL node (LTS) via nvm"
    nvm install --lts
  else
    echo "OK      node already installed via nvm ($(nvm version node))"
  fi
  # Activate node so npm is on PATH for the Copilot CLI step below (both the
  # fresh-install and already-installed branches need this).
  nvm use --lts >/dev/null 2>&1 || nvm use node >/dev/null 2>&1 || true
  set -eu
else
  echo "WARN    nvm.sh not found; skipping node/Copilot CLI install" >&2
fi

if command -v npm >/dev/null 2>&1; then
  # Check for the npm global specifically -- `command -v copilot` can be
  # shadowed by VS Code's bundled copilotCli on PATH, which would wrongly skip
  # installing the standalone GitHub Copilot CLI.
  if npm ls -g @github/copilot >/dev/null 2>&1; then
    echo "OK      GitHub Copilot CLI already installed"
  else
    echo "INSTALL GitHub Copilot CLI"
    npm install -g @github/copilot
  fi
fi

# ---------------------------------------------------------------------------
# 4. Symlinks
# ---------------------------------------------------------------------------
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
