function goenv
  set command $argv[1]
  set -e argv[1]

  switch "$command"
  case shell
    . (goenv "sh-$command" $argv|psub)
  case '*'
    command goenv "$command" $argv
  end
end
