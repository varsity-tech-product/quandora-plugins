#!/bin/sh

set -eu
umask 077

MCP_NAME='quandora'
PLUGIN_SELECTOR='quandora@quandora'
OAUTH_PORT='64361'
EXPECTED_AUTH_PREFIX='https://mcp.quandora.ai/oauth/authorize?'
EXPECTED_REDIRECT='redirect_uri=http%3A%2F%2F127.0.0.1%3A64361%2Fmcp%2Foauth%2Fcallback'

if [ "$#" -ne 3 ]; then
  echo "usage: $0 <codebuddy-bin> <config-directory> <state-directory>" >&2
  exit 64
fi

codebuddy_bin=$1
config_directory=$2
state_directory=$3
status_file="$state_directory/status.json"
temporary_status="$state_directory/.status.$$"
host_log="$state_directory/host.log"
host_pid=''
current_status='initializing'
tools_count=0
needs_auth='null'

write_status() {
  status=$1
  tools_count=$2
  needs_auth=$3
  exit_code=$4
  printf '{"status":"%s","processId":%s,"hostProcessId":%s,"port":%s,"toolsCount":%s,"needsAuth":%s,"exitCode":%s}\n' \
    "$status" "$$" "${host_pid:-null}" "$OAUTH_PORT" "$tools_count" "$needs_auth" "$exit_code" >"$temporary_status"
  /bin/mv -f "$temporary_status" "$status_file"
  current_status=$status
}

cleanup() {
  exit_code=$?
  /bin/rm -f "$temporary_status"
  if [ -n "$host_pid" ] && /bin/kill -0 "$host_pid" 2>/dev/null; then
    /bin/kill "$host_pid" 2>/dev/null || true
    wait "$host_pid" 2>/dev/null || true
  fi
  case "$current_status" in
    completed|native_ready|timed_out|host_failed|port_conflict|incompatible|oauth_request_failed|oauth_response_invalid|browser_open_failed) ;;
    *)
      if [ "$exit_code" -ne 0 ]; then
        write_status 'helper_failed' "$tools_count" "$needs_auth" "$exit_code"
      fi
      ;;
  esac
}
trap cleanup EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

if [ "$(/usr/bin/uname -s)" != 'Darwin' ]; then
  echo 'This helper supports macOS only.' >&2
  exit 69
fi

for path in "$codebuddy_bin" "$config_directory" "$state_directory"; do
  case "$path" in
    /*) ;;
    *) echo 'All paths must be absolute.' >&2; exit 64 ;;
  esac
done

if [ ! -x "$codebuddy_bin" ]; then
  echo 'The resolved WorkBuddy CLI is unavailable.' >&2
  exit 66
fi
if [ ! -d "$config_directory" ] || [ -L "$config_directory" ]; then
  echo 'The WorkBuddy configuration directory is invalid.' >&2
  exit 73
fi
if [ ! -d "$state_directory" ] || [ -L "$state_directory" ]; then
  echo 'The state directory is invalid.' >&2
  exit 73
fi
/bin/chmod 700 "$state_directory"

if /usr/sbin/lsof -nP -iTCP:"$OAUTH_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  write_status 'port_conflict' 0 null 75
  exit 75
fi

write_status 'starting' 0 null null
CODEBUDDY_CONFIG_DIR="$config_directory" \
"$codebuddy_bin" \
  --serve \
  --no-session-persistence \
  --setting-sources user \
  --channels "plugin:$PLUGIN_SELECTOR" \
  --port "$OAUTH_PORT" \
  </dev/null >"$host_log" 2>&1 &
host_pid=$!
write_status 'starting' 0 null null

ready=0
already_authorized=0
attempt=0
while [ "$attempt" -lt 30 ]; do
  status_json=$(/usr/bin/curl -fsS --max-time 3 \
    -H 'x-codebuddy-request: 1' \
    -H 'Content-Type: application/json' \
    -d '{"name":"quandora"}' \
    "http://127.0.0.1:$OAUTH_PORT/internal/mcp/status" 2>/dev/null || true)
  tools_json=$(/usr/bin/curl -fsS --max-time 3 \
    -H 'x-codebuddy-request: 1' \
    -H 'Content-Type: application/json' \
    -d '{"name":"quandora"}' \
    "http://127.0.0.1:$OAUTH_PORT/internal/mcp/listTools" 2>/dev/null || true)

  tools_count=0
  while printf '%s' "$tools_json" | /usr/bin/plutil -extract "$tools_count.name" raw -o - - >/dev/null 2>&1; do
    tools_count=$((tools_count + 1))
  done
  server_name=$(printf '%s' "$status_json" | /usr/bin/plutil -extract name raw -o - - 2>/dev/null || printf '')
  connection_status=$(printf '%s' "$status_json" | /usr/bin/plutil -extract status raw -o - - 2>/dev/null || printf '')
  needs_auth=$(printf '%s' "$status_json" | /usr/bin/plutil -extract needsAuth raw -o - - 2>/dev/null || printf 'null')
  if [ "$server_name" = "$MCP_NAME" ] && [ "$needs_auth" = 'false' ] && \
     [ "$connection_status" = 'connected' ]; then
    ready=1
    already_authorized=1
    break
  fi
  if [ "$server_name" = "$MCP_NAME" ] && [ "$connection_status" != 'disconnected' ] && \
     [ "$needs_auth" = 'true' ]; then
    ready=1
    break
  fi
  if ! /bin/kill -0 "$host_pid" 2>/dev/null; then
    write_status 'host_failed' "$tools_count" "$needs_auth" 70
    exit 70
  fi
  attempt=$((attempt + 1))
  sleep 1
done

if [ "$ready" -ne 1 ]; then
  write_status 'incompatible' "$tools_count" "$needs_auth" 69
  exit 69
fi

if [ "$already_authorized" -eq 1 ]; then
  write_status 'completed' "$tools_count" false 0
  exit 0
fi

write_status 'authorizing' "$tools_count" true null
if ! authorization_json=$(/usr/bin/curl -fsS --max-time 10 \
  -H 'x-codebuddy-request: 1' \
  -H 'Content-Type: application/json' \
  -d '{"name":"quandora"}' \
  "http://127.0.0.1:$OAUTH_PORT/internal/mcp/oauth/authorize"); then
  write_status 'oauth_request_failed' "$tools_count" true 69
  exit 69
fi
authorization_error=$(printf '%s' "$authorization_json" | /usr/bin/plutil -extract error raw -o - - 2>/dev/null || printf '')
if [ "$authorization_error" = 'No authorization URL available. Server may not require OAuth or connection attempt has not been made yet.' ]; then
  status_json=$(/usr/bin/curl -fsS --max-time 3 \
    -H 'x-codebuddy-request: 1' \
    -H 'Content-Type: application/json' \
    -d '{"name":"quandora"}' \
    "http://127.0.0.1:$OAUTH_PORT/internal/mcp/status" 2>/dev/null || true)
  server_name=$(printf '%s' "$status_json" | /usr/bin/plutil -extract name raw -o - - 2>/dev/null || printf '')
  connection_status=$(printf '%s' "$status_json" | /usr/bin/plutil -extract status raw -o - - 2>/dev/null || printf '')
  needs_auth=$(printf '%s' "$status_json" | /usr/bin/plutil -extract needsAuth raw -o - - 2>/dev/null || printf 'null')
  if [ "$server_name" = "$MCP_NAME" ] && [ "$connection_status" = 'connected' ] && \
     [ "$needs_auth" = 'false' ]; then
    write_status 'native_ready' "$tools_count" false 0
    exit 0
  fi
fi
if ! authorization_url=$(printf '%s' "$authorization_json" | /usr/bin/plutil -extract authorizationUrl raw -o - - 2>/dev/null); then
  write_status 'oauth_response_invalid' "$tools_count" true 65
  exit 65
fi
case "$authorization_url" in
  "$EXPECTED_AUTH_PREFIX"*) ;;
  *) write_status 'oauth_response_invalid' "$tools_count" true 65; exit 65 ;;
esac
case "$authorization_url" in
  *"$EXPECTED_REDIRECT"*) ;;
  *) write_status 'oauth_response_invalid' "$tools_count" true 65; exit 65 ;;
esac
if ! /usr/bin/open "$authorization_url"; then
  write_status 'browser_open_failed' "$tools_count" true 69
  exit 69
fi
unset authorization_url authorization_json

attempt=0
while [ "$attempt" -lt 300 ]; do
  status_json=$(/usr/bin/curl -fsS --max-time 3 \
    -H 'x-codebuddy-request: 1' \
    -H 'Content-Type: application/json' \
    -d '{"name":"quandora"}' \
    "http://127.0.0.1:$OAUTH_PORT/internal/mcp/status" 2>/dev/null || true)
  needs_auth=$(printf '%s' "$status_json" | /usr/bin/plutil -extract needsAuth raw -o - - 2>/dev/null || printf 'null')
  connection_status=$(printf '%s' "$status_json" | /usr/bin/plutil -extract status raw -o - - 2>/dev/null || printf '')
  server_name=$(printf '%s' "$status_json" | /usr/bin/plutil -extract name raw -o - - 2>/dev/null || printf '')
  tools_json=$(/usr/bin/curl -fsS --max-time 3 \
    -H 'x-codebuddy-request: 1' \
    -H 'Content-Type: application/json' \
    -d '{"name":"quandora"}' \
    "http://127.0.0.1:$OAUTH_PORT/internal/mcp/listTools" 2>/dev/null || true)
  tools_count=0
  while printf '%s' "$tools_json" | /usr/bin/plutil -extract "$tools_count.name" raw -o - - >/dev/null 2>&1; do
    tools_count=$((tools_count + 1))
  done
  if [ "$server_name" = "$MCP_NAME" ] && [ "$needs_auth" = 'false' ] && \
     [ "$connection_status" = 'connected' ]; then
    write_status 'completed' "$tools_count" false 0
    exit 0
  fi
  if ! /bin/kill -0 "$host_pid" 2>/dev/null; then
    write_status 'host_failed' "$tools_count" "$needs_auth" 70
    exit 70
  fi
  attempt=$((attempt + 1))
  sleep 1
done

write_status 'timed_out' "$tools_count" "$needs_auth" 124
exit 124
