function killer
    pgrep -f $argv[1] | xargs kill -KILL
end
