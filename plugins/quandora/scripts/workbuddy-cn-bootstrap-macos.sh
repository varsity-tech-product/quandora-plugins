#!/bin/sh

set -eu
umask 077

readonly BUNDLE_ID='com.tencent.workbuddy.mac'
readonly TEAM_ID='FN2V63AD2J'
readonly URL_SCHEME='workbuddy'
readonly SCRIPT_BASE_DEFAULT='https://raw.githubusercontent.com/varsity-tech-product/quandora-plugins/main/plugins/quandora/scripts'
readonly INSTALLER_SHA256='19a25e59fe401b7ac339295e159dab42a96c70b67711905db90d6314314fa187'
readonly OAUTH_SHA256='65db30362772d399a95bd278810c027a39efddf6e70f80bea475d851d4b8c51b'
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

valid_workbuddy_app() {
  candidate=$1
  info_plist="$candidate/Contents/Info.plist"
  [ -d "$candidate" ] || return 1
  [ -f "$info_plist" ] || return 1
  [ "$(plist_value "$info_plist" CFBundleIdentifier || :)" = "$BUNDLE_ID" ] || return 1
  [ "$(plist_value "$info_plist" CFBundleURLTypes.0.CFBundleURLSchemes.0 || :)" = "$URL_SCHEME" ] || return 1
  signature_details=$(/usr/bin/codesign -dv --verbose=4 "$candidate" 2>&1) || return 1
  signing_identifier=$(printf '%s\n' "$signature_details" | /usr/bin/awk -F= '$1 == "Identifier" { print $2; exit }')
  team_identifier=$(printf '%s\n' "$signature_details" | /usr/bin/awk -F= '$1 == "TeamIdentifier" { print $2; exit }')
  [ "$signing_identifier" = "$BUNDLE_ID" ] || return 1
  [ "$team_identifier" = "$TEAM_ID" ] || return 1

  # WorkBuddy may create runtime cache files inside its sealed bundle. Verify its
  # Developer ID signature and executable code while ignoring only resource drift.
  /usr/bin/codesign --verify --strict --ignore-resources "$candidate" >/dev/null 2>&1 || return 1
}

resolve_workbuddy_app() {
  if [ -n "${QUANDORA_WORKBUDDY_APP:-}" ]; then
    resolved=$(canonical_directory "$QUANDORA_WORKBUDDY_APP" || :)
    if [ -z "$resolved" ] || ! valid_workbuddy_app "$resolved"; then
      fail \
        'invalid_host' \
        'The selected application is not a valid signed WorkBuddy China bundle.' \
        'Install or update WorkBuddy from https://www.codebuddy.cn/work/ and retry in a new local Agent task.'
    fi
    printf '%s\n' "$resolved"
    return
  fi

  registered=$(/usr/bin/osascript -e 'POSIX path of (path to application id "com.tencent.workbuddy.mac")' 2>/dev/null || :)
  if [ -n "$registered" ]; then
    resolved=$(canonical_directory "$registered" || :)
    if [ -n "$resolved" ] && valid_workbuddy_app "$resolved"; then
      printf '%s\n' "$resolved"
      return
    fi
  fi

  for candidate in '/Applications/WorkBuddy.app' "$HOME/Applications/WorkBuddy.app"; do
    resolved=$(canonical_directory "$candidate" || :)
    if [ -n "$resolved" ] && valid_workbuddy_app "$resolved"; then
      printf '%s\n' "$resolved"
      return
    fi
  done

  fail \
    'host_update_required' \
    'A signed local WorkBuddy China application could not be found.' \
    'Install the correct Apple Silicon or Intel build from https://www.codebuddy.cn/work/, sign in, and retry in a new local Agent task.'
}

resolve_config_root() {
  if [ -n "${CODEBUDDY_CONFIG_DIR:-}" ]; then
    candidate=$CODEBUDDY_CONFIG_DIR
  else
    candidate="$HOME/.workbuddy"
  fi
  resolved=$(canonical_directory "$candidate" || :)
  if [ -z "$resolved" ] || [ ! -f "$resolved/storage/skeleton/account-snapshot.json" ]; then
    fail \
      'host_login_required' \
      'The active WorkBuddy account configuration is unavailable.' \
      'Sign in to the local WorkBuddy China application, start a new Agent task, and retry the same installation prompt.'
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
    'This Quandora installer supports local macOS WorkBuddy China Agent tasks only.' \
    'Open the installation prompt in WorkBuddy China on a supported Mac.'
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
config_root=$(resolve_config_root)
electron="$app_root/Contents/MacOS/Electron"
cli="$app_root/Contents/Resources/app.asar.unpacked/cli/bin/codebuddy"

if [ ! -x "$electron" ] || [ ! -x "$cli" ]; then
  fail \
    'host_update_required' \
    'The selected WorkBuddy application does not expose its required bundled runtime and plugin manager.' \
    'In WorkBuddy open Personal Center, choose Check for Updates, complete the update, restart WorkBuddy, and retry in a new Agent task.'
fi

script_directory=$(canonical_directory "$(/usr/bin/dirname "$0")" || :)
if [ -z "$script_directory" ]; then
  fail \
    'invalid_bootstrap' \
    'The reviewed Quandora bootstrap directory is unavailable.' \
    'Download the bootstrap again through the canonical installation guide.'
fi
installer="$script_directory/workbuddy-cn-install-macos.js"
oauth="$script_directory/workbuddy-cn-oauth-macos.js"
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
download_reviewed_script \
  "$script_base/workbuddy-cn-oauth-macos.js" \
  "$oauth" \
  "$OAUTH_SHA256"

ELECTRON_RUN_AS_NODE=1 "$electron" "$installer" "$app_root" "$config_root"
