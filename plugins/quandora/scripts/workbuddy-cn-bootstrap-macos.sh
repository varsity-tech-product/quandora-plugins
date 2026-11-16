#!/bin/sh

set -eu
umask 077

# WorkBuddy China and WorkBuddy AI (international) share Tencent's Developer ID team.
readonly SUPPORTED_BUNDLE_IDS='com.tencent.workbuddy.mac com.workbuddy.workbuddy-ai'
readonly TEAM_ID='FN2V63AD2J'
readonly SCRIPT_BASE_DEFAULT='https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/plugins/quandora/scripts'
readonly INSTALLER_SHA256='612d918e948539240c60b288097de76ea553df484742bc0c6fbbace1828b79e6'
readonly MAX_SCRIPT_BYTES=1048576

fail() {
  code=$1
  message=$2
  remediation=$3
  printf '{"status":"failed","code":"%s","message":"%s","remediation":"%s"}\n' \
    "$code" "$message" "$remediation" >&2
  exit 69
}

canonical_directory() {
  directory=$1
  (CDPATH= cd -P "$directory" 2>/dev/null && /bin/pwd -P)
}

plist_value() {
  plist=$1
  key=$2
  /usr/bin/plutil -extract "$key" raw -o - "$plist" 2>/dev/null
}

supported_bundle_id() {
  case "$1" in
    com.tencent.workbuddy.mac|com.workbuddy.workbuddy-ai) return 0 ;;
    *) return 1 ;;
  esac
}

valid_workbuddy_app() {
  candidate=$1
  info_plist="$candidate/Contents/Info.plist"
  [ -d "$candidate" ] || return 1
  [ -f "$info_plist" ] || return 1
  app_bundle_id=$(plist_value "$info_plist" CFBundleIdentifier || :)
  supported_bundle_id "$app_bundle_id" || return 1
  signature_details=$(/usr/bin/codesign -dv --verbose=4 "$candidate" 2>&1) || return 1
  signing_identifier=$(printf '%s\n' "$signature_details" | /usr/bin/awk -F= '$1 == "Identifier" { print $2; exit }')
  team_identifier=$(printf '%s\n' "$signature_details" | /usr/bin/awk -F= '$1 == "TeamIdentifier" { print $2; exit }')
  [ "$signing_identifier" = "$app_bundle_id" ] || return 1
  [ "$team_identifier" = "$TEAM_ID" ] || return 1

  # WorkBuddy may create runtime cache files inside its sealed bundle. Verify its
  # Developer ID signature and executable code while ignoring only resource drift.
  /usr/bin/codesign --verify --strict --ignore-resources "$candidate" >/dev/null 2>&1 || return 1
}

# The WorkBuddy application that launched this Agent task, from the location it
# passes to its Agent shell. Empty when the variable is absent or invalid.
host_workbuddy_app() {
  [ -n "${WORKBUDDY_RESOURCES_PATH:-}" ] || return 0
  host_app=$(canonical_directory "${WORKBUDDY_RESOURCES_PATH%/}/../.." || :)
  if [ -n "$host_app" ] && valid_workbuddy_app "$host_app"; then
    printf '%s\n' "$host_app"
  fi
}

resolve_workbuddy_app() {
  if [ -n "${QUANDORA_WORKBUDDY_APP:-}" ]; then
    resolved=$(canonical_directory "$QUANDORA_WORKBUDDY_APP" || :)
    if [ -z "$resolved" ] || ! valid_workbuddy_app "$resolved"; then
      fail \
        'invalid_host' \
        'The selected application is not a valid signed WorkBuddy bundle.' \
        'Install or update WorkBuddy through its official download page and retry in a new local Agent task.'
    fi
    printf '%s\n' "$resolved"
    return
  fi

  resolved=$(host_workbuddy_app)
  if [ -n "$resolved" ]; then
    printf '%s\n' "$resolved"
    return
  fi

  for registered_id in $SUPPORTED_BUNDLE_IDS; do
    registered=$(/usr/bin/osascript -e "POSIX path of (path to application id \"$registered_id\")" 2>/dev/null || :)
    if [ -n "$registered" ]; then
      resolved=$(canonical_directory "$registered" || :)
      if [ -n "$resolved" ] && valid_workbuddy_app "$resolved"; then
        printf '%s\n' "$resolved"
        return
      fi
    fi
  done

  for candidate in \
    '/Applications/WorkBuddy.app' \
    "$HOME/Applications/WorkBuddy.app" \
    '/Applications/WorkBuddy AI.app' \
    "$HOME/Applications/WorkBuddy AI.app"
  do
    resolved=$(canonical_directory "$candidate" || :)
    if [ -n "$resolved" ] && valid_workbuddy_app "$resolved"; then
      printf '%s\n' "$resolved"
      return
    fi
  done

  fail \
    'host_update_required' \
    'A signed local WorkBuddy application could not be found.' \
    'Install the correct Apple Silicon or Intel build of WorkBuddy (China edition: https://www.codebuddy.cn/work/) or WorkBuddy AI, sign in, and retry in a new local Agent task.'
}

resolve_config_root() {
  app_root=$1
  candidate=''
  if [ -n "${WORKBUDDY_CONFIG_DIR:-}" ] && [ "$(host_workbuddy_app)" = "$app_root" ]; then
    candidate=$WORKBUDDY_CONFIG_DIR
  elif [ -n "${CODEBUDDY_CONFIG_DIR:-}" ]; then
    candidate=$CODEBUDDY_CONFIG_DIR
  else
    case "$(plist_value "$app_root/Contents/Info.plist" CFBundleIdentifier || :)" in
      com.workbuddy.workbuddy-ai) candidate="$HOME/.workbuddy-ai" ;;
      *) candidate="$HOME/.workbuddy" ;;
    esac
  fi
  resolved=$(canonical_directory "$candidate" || :)
  if [ -z "$resolved" ]; then
    fail \
      'host_login_required' \
      'The active WorkBuddy configuration is unavailable.' \
      'Sign in to the local WorkBuddy application, start a new Agent task, and retry the same installation prompt.'
  fi
  printf '%s\n' "$resolved"
}

download_reviewed_script() {
  url=$1
  destination=$2
  expected_sha=$3

  /usr/bin/curl \
    --proto '=https' \
    --tlsv1.2 \
    --location \
    --fail \
    --silent \
    --show-error \
    --output "$destination" \
    "$url" || fail \
      'download_failed' \
      'A reviewed Quandora installer component could not be downloaded.' \
      'Check access to raw.githubusercontent.com, then retry once after the failed process has exited.'

  byte_count=$(/usr/bin/wc -c <"$destination" | /usr/bin/tr -d ' ')
  if [ -z "$byte_count" ] || [ "$byte_count" -le 0 ] || [ "$byte_count" -gt "$MAX_SCRIPT_BYTES" ]; then
    fail \
      'integrity_failed' \
      'A downloaded Quandora installer component has an invalid size.' \
      'Stop without executing it and retry only after the production repository is verified.'
  fi

  actual_sha=$(/usr/bin/shasum -a 256 "$destination" | /usr/bin/awk '{print $1}')
  if [ "$actual_sha" != "$expected_sha" ]; then
    fail \
      'integrity_failed' \
      'A downloaded Quandora installer component failed its SHA-256 check.' \
      'Stop without executing it and retry only after the production repository is verified.'
  fi
  /bin/chmod 600 "$destination"
}

if [ "$(/usr/bin/uname -s)" != 'Darwin' ]; then
  fail \
    'unsupported_host' \
    'This Quandora installer supports local macOS WorkBuddy Agent tasks only.' \
    'Install Quandora from WorkBuddy plugin settings, or open the installation prompt in WorkBuddy on a supported Mac.'
fi

for required_tool in \
  /bin/chmod \
  /bin/pwd \
  /usr/bin/awk \
  /usr/bin/codesign \
  /usr/bin/curl \
  /usr/bin/dirname \
  /usr/bin/osascript \
  /usr/bin/plutil \
  /usr/bin/shasum \
  /usr/bin/tr \
  /usr/bin/uname \
  /usr/bin/wc
do
  [ -x "$required_tool" ] || fail \
    'host_update_required' \
    'A required macOS system utility is unavailable.' \
    'Update macOS and WorkBuddy through their official update flows, then retry in a new local Agent task.'
done

app_root=$(resolve_workbuddy_app)
config_root=$(resolve_config_root "$app_root")
executable_name=$(plist_value "$app_root/Contents/Info.plist" CFBundleExecutable || :)
case "$executable_name" in
  ''|*/*) executable_name='' ;;
esac
electron="$app_root/Contents/MacOS/$executable_name"
cli="$app_root/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy"

if [ -z "$executable_name" ] || [ ! -x "$electron" ] || [ ! -x "$cli" ]; then
  fail \
    'host_layout_unsupported' \
    'This WorkBuddy build does not expose the bundled runtime and plugin manager this installer uses.' \
    'Install Quandora from WorkBuddy plugin settings instead, then complete WorkBuddy authorization.'
fi

script_directory=$(canonical_directory "$(/usr/bin/dirname "$0")" || :)
if [ -z "$script_directory" ]; then
  fail \
    'invalid_bootstrap' \
    'The reviewed Quandora bootstrap directory is unavailable.' \
    'Download the bootstrap again through the canonical installation guide.'
fi
installer="$script_directory/workbuddy-cn-install-macos.js"
script_base=${QUANDORA_WORKBUDDY_SCRIPT_BASE_URL:-$SCRIPT_BASE_DEFAULT}
case "$script_base" in
  https://*) ;;
  *)
    fail \
      'invalid_source' \
      'The Quandora installer source must use HTTPS.' \
      'Use the canonical production installation guide without changing its source.'
    ;;
esac
script_base=${script_base%/}

download_reviewed_script \
  "$script_base/workbuddy-cn-install-macos.js" \
  "$installer" \
  "$INSTALLER_SHA256"

ELECTRON_RUN_AS_NODE=1 "$electron" "$installer" "$app_root" "$config_root"
