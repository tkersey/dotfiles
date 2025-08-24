if not command -s goenv > /dev/null
    echo "goenv: command not found. See https://github.com/wfarr/goenv"
    exit 1
end

set -l goenv_root ''
if test -z "$GOENV_ROOT"
    set goenv_root "$HOME/.goenv"
    set -x GOENV_ROOT "$HOME/.goenv"
else
    set goenv_root "$GOENV_ROOT"
end

set -x PATH $goenv_root/shims $PATH
set -x GOENV_SHELL fish
if test ! -d "$goenv_root/shims"; or test ! -d "$goenv_root/versions"
    command mkdir -p $goenv_root/{shims,versions}
end
