function __native_prompt_context --argument-names item --description 'Conditional language and environment context'
    set -l parents $argv[2..-1]

    switch $item
        case aws
            command --query aws; or return
            set -l profile "$AWS_DEFAULT_PROFILE"
            set -l region "$AWS_DEFAULT_REGION"
            set -q AWS_PROFILE; and set profile "$AWS_PROFILE"
            set -q AWS_REGION; and set region "$AWS_REGION"
            set -l context (string join / -- (string match --entire --regex '.+' -- "$profile" "$region"))
            test -n "$context"; and __native_prompt_segment FF9900 " $context"
            return
        case kubectl
            command --query kubectl; or return
            set -l context (command kubectl config view --minify \
                --output 'jsonpath={.current-context}/{..namespace}' 2>/dev/null)
            or return
            set context (string replace --regex '/(|default)$' '' -- "$context")
            test -n "$context"; and __native_prompt_segment 326CE5 "󱃾 $context"
            return
    end

    set -l executable "$item"
    set -l arguments --version
    set -l markers
    set -l color
    set -l icon
    set -l environment_name ''
    switch $item
        case node
            set markers package.json
            set color 44883E
            set icon ''
        case python
            set executable python3
            command --query python3; or set executable python
            set markers .python-version Pipfile __init__.py pyproject.toml requirements.txt setup.py
            # The saved Python module only checks the current directory unless
            # a virtual environment is active; preserve that activation rule.
            set parents "$PWD"
            set color 00AFAF
            set icon '󰌠'
            if test -n "$VIRTUAL_ENV"
                set -l parts (string split / -- (string trim --right --chars=/ -- "$VIRTUAL_ENV"))
                set environment_name "$parts[-1]"
                if set -q parts[-2]
                    if test "$parts[-2]" = virtualenvs
                        set environment_name (string replace --regex '-[^-]+$' '' -- "$environment_name")
                    else if contains -- "$environment_name" virtualenv venv .venv env
                        set environment_name "$parts[-2]"
                    end
                end
            end
        case java
            set arguments -version
            set markers pom.xml
            set color ED8B00
            set icon ''
        case ruby
            set markers Gemfile Rakefile .ruby-version
            set color B31209
            set icon ''
        case go
            set arguments version
            set markers go.mod
            set color 00ACD7
            set icon ''
        case zig
            set arguments version
            set markers build.zig
            set color F7A41D
            set icon ''
        case rustc
            set markers Cargo.toml
            set color F74C00
            set icon ''
        case php
            set markers composer.json
            set color 617CBE
            set icon ''
        case crystal
            set markers shard.yml
            set color FFFFFF
            set icon ''
        case elixir
            set markers mix.exs
            set color 4E2A8E
            set icon ''
        case '*'
            return
    end
    command --query "$executable"; or return

    set -l active false
    test -n "$environment_name"; and set active true
    for directory in $parents
        for marker in $markers
            if test -e "$directory/$marker"
                set active true
                break
            end
        end
        if test "$item" = ruby
            # Wildcard expansion is allowed to be empty in a set command.
            set -l gemspecs "$directory"/*.gemspec
            set -q gemspecs[1]; and set active true
        end
        test "$active" = true; and break
    end
    test "$active" = true; or return

    # Only invoke an installed runtime in its corresponding project context.
    # No application code is sourced or evaluated by the prompt.
    set -l output (command "$executable" $arguments 2>&1)
    or return
    set -q output[1]; or return
    if test "$item" = elixir
        set output (string match --entire --regex '^Elixir ' -- $output)
    end
    set -q output[1]; or return
    set -l versions (string match --regex -- '[0-9]+(?:\.[0-9]+)+(?:[-+][A-Za-z0-9.+-]+)?' $output)
    set -q versions[1]; or return
    set -l text "$icon $versions[1]"
    test -n "$environment_name"; and set text "$text ($environment_name)"
    __native_prompt_segment $color "$text"
end
