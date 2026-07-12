  # Homebrew: put /opt/homebrew/bin (nvim, tmux, git, …) on PATH.
  if [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [ -x /usr/local/bin/brew ]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi

  export NVM_DIR="$HOME/.nvm"
  [ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"  # This loads nvm
  [ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"  # This loads nvm bash_completion

  alias vim='nvim'
  alias vi='nvim'
  alias ai='copilot'

  # Prefer ~/Documents/Git, fall back to ~/Git, else stay put.
  for _gitdir in ~/Documents/Git ~/Git; do
    [ -d "$_gitdir" ] && cd "$_gitdir" && break
  done
  unset _gitdir
