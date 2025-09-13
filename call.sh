# set tmp env variables to proxy claude-code calls
export ANTHROPIC_BASE_URL=http://localhost:7187
export ANTHROPIC_API_KEY=NOT_NEEDED

# path to where claude-code should be located
$HOME/.claude/local/claude "$@"

# remove tmp env variables after everything
unset ANTHROPIC_BASE_URL
unset ANTHROPIC_API_KEY
