#function gi() { curl -s https://www.gitignore.io/api/${(j:,:)@} ;}
function check_ssh {
  [[ $3 =~ '\bssh\b' ]] || return
  [[ -n "$SSH_AGENT_PID" && -e "/proc/$SSH_AGENT_PID" ]] && ssh-add -l >/dev/null && return
  eval `keychain --eval id_dsa --timeout 60`
}
