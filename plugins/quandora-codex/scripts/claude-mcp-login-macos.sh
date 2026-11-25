#!/bin/sh

set -eu
umask 077

MCP_IDENTITY='plugin:quandora:quandora'

if [ "$#" -ne 2 ]; then
  echo "usage: $0 <claude-bin> <state-directory>" >&2
  exit 64
fi

claude_bin=$1
state_directory=$2
status_file="$state_directory/status.json"
temporary_status="$state_directory/.status.$$"

cleanup() {
  /bin/rm -f "$temporary_status"
}
trap cleanup EXIT HUP INT TERM

write_status() {
  status=$1
  exit_code=$2
  completed_at=$3
  printf '{"status":"%s","processId":%s,"exitCode":%s,"completedAt":%s}\n' \
    "$status" "$$" "$exit_code" "$completed_at" > "$temporary_status"
  /bin/mv -f "$temporary_status" "$status_file"
}

if [ "$(/usr/bin/uname -s)" != 'Darwin' ]; then
  echo 'This helper supports macOS only.' >&2
  exit 69
fi

if [ ! -x "$claude_bin" ]; then
  echo 'The resolved Claude Code executable is not executable.' >&2
  exit 66
fi

case "$state_directory" in
  /*) ;;
  *)
    echo 'The state directory must be an absolute path.' >&2
    exit 64
    ;;
esac

if [ ! -d "$state_directory" ] || [ -L "$state_directory" ]; then
  echo 'The state directory must be an existing non-symlink directory.' >&2
  exit 73
fi

/bin/chmod 700 "$state_directory"

if [ ! -x /usr/bin/script ]; then
  write_status 'unsupported' 69 null
  exit 69
fi

if ! "$claude_bin" mcp help login >/dev/null 2>&1; then
  completed_at="\"$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')\""
  write_status 'incompatible_cli' 69 "$completed_at"
  exit 69
fi

write_status 'running' null null

set +e
/usr/bin/script -q /dev/null /bin/sh -c \
  'test -t 0 && test -t 1 || exit 70; exec "$1" mcp login "$2"' \
  quandora-claude-login "$claude_bin" "$MCP_IDENTITY" >/dev/null 2>&1
exit_code=$?
set -e

completed_at="\"$(/bin/date -u '+%Y-%m-%dT%H:%M:%SZ')\""
if [ "$exit_code" -eq 0 ]; then
  write_status 'completed' "$exit_code" "$completed_at"
elif [ "$exit_code" -eq 70 ]; then
  write_status 'no_interactive_pty' "$exit_code" "$completed_at"
else
  write_status 'failed' "$exit_code" "$completed_at"
fi

exit "$exit_code"
