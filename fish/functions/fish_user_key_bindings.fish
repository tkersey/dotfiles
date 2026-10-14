function fish_user_key_bindings
  fzf_key_bindings
  for mode in insert default visual
    bind --mode $mode ctrl-alt-p __native_prompt_toggle_details
  end
end
