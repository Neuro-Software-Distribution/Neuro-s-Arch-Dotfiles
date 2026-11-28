#!/usr/bin/env bash
#### Check for updates from remote repo and installs
set -uo pipefail
THEME="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ORIGIN="$(git -C "$THEME" remote get-url origin 2>/dev/null || true)"
REPO="$(printf '%s' "$ORIGIN" | sed -nE 's#^(https://github.com/|git@github.com:|ssh://git@github.com/)([^/]+/[^/]+)$#\2#p')"
REPO="${REPO%.git}"
API="https://api.github.com/repos/$REPO/releases/latest"
USER_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/cyberarch"
CACHE="$USER_DIR/update.json"
APPLIED="$USER_DIR/applied-version"
APPLIED_COMMIT="$USER_DIR/applied-commit"
STAMP="$USER_DIR/update-done"

R=$'\033[0m'; B=$'\033[1m'; DIM=$'\033[2m'
RED=$'\033[38;2;255;45;61m'; CYAN=$'\033[38;2;119;226;242m'
YEL=$'\033[38;2;255;214;31m'; GRN=$'\033[38;2;90;230;130m'; GREY=$'\033[38;2;120;120;130m'
line()  { printf "${RED}%s${R}\n" "────────────────────────────────────────────────────────────"; }
hdr()   { printf "\n${CYAN}${B}▓▒░ %s ░▒▓${R}\n" "$1"; }
step()  { printf "${CYAN}▸${R} %s\n" "$1"; }
ok()    { printf "  ${GRN}✓${R} %s\n" "$1"; }
warn()  { printf "  ${YEL}⚠${R} %s\n" "$1"; }
err()   { printf "  ${RED}✗${R} %s\n" "$1"; }
banner() {
  printf "${RED}${B}"
  cat <<'EOF'
   █▀▀ █▄█ █▄▄ █▀▀ █▀█ ▄▀█ █▀█ █▀▀ █_█    █░█ █▀█ █▀▄ ▄▀█ ▀█▀ █▀▀
   █▄▄ ░█░ █▄█ ██▄ █▀▄ █▀█ █▀▄ █▄▄ █░█    █▄█ █▀▀ █▄▀ █▀█ ░█░ ██▄
EOF
  printf "${R}${CYAN}   ░▒▓ N E T R U N N E R * Updater ▓▒░${R}\n"
  line
}

norm() { printf '%s' "${1#[vV]}" | tr -d '[:space:]'; }

# Greek major versions map to 1–24, so beta.46 equals 2.46. The
# remaining components are numeric, exactly as for existing version tags.
version_key() {
    local version major tail i
    local -a names=(alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega)
    local -a letters=(α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω)
    version="$(norm "${1:-}")"
    [[ "$version" =~ ^([^.]+)(\.[0-9]+){0,3}$ ]] || return 1
    major="${version%%.*}"
    tail="${version#"$major"}"
    if [[ ! "$major" =~ ^[0-9]+$ ]]; then
        for i in "${!names[@]}"; do
            if [[ "$major" = "${names[$i]}" || "$major" = "${letters[$i]}" ]]; then
                major=$((i + 1))
                break
            fi
        done
        [[ "$major" =~ ^[0-9]+$ ]] || return 1
    fi
    printf '%s%s\n' "$major" "$tail"
}

vlt() {
    local a b
    a="$(version_key "${1:-}")" || return 2
    b="$(version_key "${2:-}")" || return 2
    awk -v a="$a" -v b="$b" '
        BEGIN {
            split(a, x, "."); split(b, y, ".")
            for (i = 1; i <= 4; i++) {
                if (x[i] + 0 < y[i] + 0) exit 0
                if (x[i] + 0 > y[i] + 0) exit 1
            }
            exit 1
        }'
}

local_ver() {
    v=""
    [ -r "$THEME/VERSION" ] && read -r v < "$THEME/VERSION"
    v="$(norm "${v:-0.0.0}")"
    [ -n "$v" ] || v="0.0.0"
    if [ -r "$APPLIED" ] && [ -r "$APPLIED_COMMIT" ] && [ "$(cat "$APPLIED_COMMIT")" = "$(git -C "$THEME" rev-parse HEAD 2>/dev/null)" ]; then
        a=""
        read -r a < "$APPLIED"
        a="$(norm "${a:-}")"
        [ -n "$a" ] && vlt "$v" "$a" && v="$a"
    fi
    printf '%s\n' "$v"
}
remote_tag() { jq -r --arg repo "$REPO" 'select(._cyberarch_repo == $repo) | .tag_name // empty' "$CACHE" 2>/dev/null; }
fetch_release() {
    local response status curl_status
    [ -n "$REPO" ] || { err "Origin must be a supported GitHub URL." >&2; return 1; }
    command -v curl >/dev/null 2>&1 || { err "curl is required for release lookup." >&2; return 1; }
    command -v jq >/dev/null 2>&1 || { err "jq is required for release lookup." >&2; return 1; }
    response="$(mktemp)" || return 1
    status="$(curl -sSL --max-time 8 -H 'Accept: application/vnd.github+json' -o "$response" -w '%{http_code}' "$API")" && curl_status=0 || curl_status=$?
    if [ "$curl_status" -ne 0 ]; then
        rm -f "$response"
        err "Could not contact GitHub (curl exit $curl_status)." >&2
        return 1
    fi
    if [ "$status" != 200 ]; then
        rm -f "$response"
        if [ "$status" = 404 ]; then
            err "No published stable release found for $REPO (or the repository is inaccessible)." >&2
            err "Publish a GitHub release with a version tag; release assets are not required." >&2
        else
            err "GitHub release lookup returned HTTP $status." >&2
        fi
        return 1
    fi
    if ! jq -e '.tag_name | strings | select(length > 0)' "$response" >/dev/null 2>&1; then
        rm -f "$response"
        err "GitHub returned an invalid release response." >&2
        return 1
    fi
    mkdir -p "$USER_DIR"
    jq --arg repo "$REPO" '. + {_cyberarch_repo: $repo}' "$response" > "$CACHE"
    local result=$?
    rm -f "$response"
    return "$result"
}

cmd_check() {    lv="$(local_ver)"
    if [ "${1:-}" = "--cached" ]; then
  [ -r "$CACHE" ] || { printf '0\n%s\n%s\n' "$lv" "$lv"; return 0; }
    else
  fetch_release 2>/dev/null || { printf '0\n%s\n%s\n' "$lv" "$lv"; return 0; }
    fi
     rv="$(norm "$(remote_tag)")"
      [ -n "$rv" ] || { printf '0\n%s\n%s\n' "$lv" "$lv"; return 0; }
    if vlt "$lv" "$rv"; then
        printf '1\n%s\n%s\n' "$lv" "$rv"
        jq -r '.body // empty' "$CACHE" 2>/dev/null | tr -d '\r'
    else
        printf '0\n%s\n%s\n' "$lv" "$rv"
    fi }

cmd_spawn() {


    run="'$THEME/updater.sh'; ec=\$?; echo; printf '\033[1;36m>> update finished (exit %s). press ENTER to close.\033[0m ' \"\$ec\"; read _"
    command -v kitty >/dev/null 2>&1 || { notify-send "CyberArch update" "Kitty is required" 2>/dev/null; return 1; }
    setsid kitty --title "CYBERARCH UPDATE" sh -c "$run" >/dev/null 2>&1 &

}

cmd_apply() (
    set -euo pipefail
    command -v git >/dev/null || { err "git is required"; exit 1; }
    git -C "$THEME" rev-parse --is-inside-work-tree >/dev/null || {
        err "This is a packaged installation; update it through the package manager."; exit 1;
    }
    [ -w "$THEME" ] && [ "$(id -u)" != 0 ] || {
        err "Do not run the desktop updater as root; use the distro package manager."; exit 1;
    }
    mkdir -p "$USER_DIR"
    exec 9>"$USER_DIR/.update.lock"
    flock -n 9 || { err "Another update is running"; exit 1; }
    cd "$THEME"
    [ -z "$(git status --porcelain --untracked-files=all)" ] || {
        err "Commit or back up local changes before updating. Nothing was stashed or removed."; exit 1;
    }
    fetch_release || { err "Release lookup failed; no branch fallback was applied."; exit 1; }
    tag="$(remote_tag)"
    git check-ref-format "refs/tags/$tag" && version_key "$tag" >/dev/null || { err "Invalid release version: $tag"; exit 1; }
    version_key "$(local_ver)" >/dev/null || { err "Invalid installed version"; exit 1; }
    rv="$(norm "$tag")"
    vlt "$(local_ver)" "$rv" || { ok "Already up to date"; exit 0; }
    OLD="$(git rev-parse HEAD)"
    git fetch origin "refs/tags/$tag"
    target="$(git rev-parse 'FETCH_HEAD^{commit}')"
    git merge-base --is-ancestor "$OLD" "$target" || { err "Release is not a fast-forward"; exit 1; }
    # Installer/dependency changes require an explicit install/package upgrade,
    # before the running checkout is touched.
    git diff --quiet "$OLD" "$target" -- install.sh package.json packaging || {
        err "This release changes installation/dependencies. Install the release in a separate checkout, or upgrade its distro package."; exit 1;
    }
    stage="$(mktemp -d)"
    activated=false
    committed=false
    cleanup() {
        result=$?
        trap - EXIT INT TERM
        if "$activated" && ! "$committed"; then
            err "Update failed; restoring the previous checkout"
            if git reset --keep "$OLD"; then
                "$THEME/scripts/restart" || err "Previous shell could not restart; inspect its log"
            else
                err "Rollback would overwrite concurrent edits. Restore $OLD after saving those edits."
            fi
        fi
        git worktree remove --force "$stage/tree" >/dev/null 2>&1 || true
        rm -rf "$stage"
        exit "$result"
    }
    trap cleanup EXIT
    trap 'exit 130' INT
    trap 'exit 143' TERM
    git worktree add --detach "$stage/tree" "$target"
    # System Astal module links are shared read-only for compilation.
    [ ! -d "$THEME/node_modules" ] || ln -s "$THEME/node_modules" "$stage/tree/node_modules"
    "$stage/tree/scripts/preflight" "$stage/build"
    [ -z "$(git status --porcelain --untracked-files=all)" ] || { err "Checkout changed during preflight"; exit 1; }
    git merge --ff-only "$target"
    activated=true
    "$THEME/scripts/restart"
    # Readiness is checked synchronously by restart. Publish commit last.
    printf '%s\n' "$rv" > "$APPLIED.new"
    printf '%s\n' "$target" > "$APPLIED_COMMIT.new"
    mv -f "$APPLIED.new" "$APPLIED"
    mv -f "$APPLIED_COMMIT.new" "$APPLIED_COMMIT"
    committed=true
    printf '%s\n' "$rv" > "$STAMP"
    ok "Release $tag is running and healthy"
)

case "${1:-}" in
    check)      shift; cmd_check "${1:-}" ;;
    --spawn)    cmd_spawn ;;
    ""|apply)   cmd_apply ;;
    *)          printf 'usage: updater.sh [check [--cached] | --spawn | apply]\n' >&2; exit 2 ;;
esac
exit

