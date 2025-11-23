#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:-11.1.0}"
DEST="${DEST:-vendor}"
CUSTOM_URL="${PILLOW_WHEEL_URL:-}"  # optional direct wheel URL override

mkdir -p "$DEST"

if ls "${DEST}"/Pillow-*.whl >/dev/null 2>&1; then
  echo "Pillow wheel already present in ${DEST}; skipping download." >&2
  exit 0
fi

# Helper to run pip download against a specific index URL.
pip_download() {
  local index_url="$1"
  echo "Trying pip download from ${index_url}..." >&2
  python -m pip download --only-binary=:all: --no-deps --dest "$DEST" --index-url "$index_url" "Pillow==${VERSION}"
}

# 1) Try PyPI over HTTPS.
if pip_download "https://pypi.org/simple"; then
  exit 0
fi

# 2) Try PyPI over HTTP.
if pip_download "http://pypi.org/simple"; then
  exit 0
fi

# 3) Try an alternate mirror that sometimes bypasses proxies.
if pip_download "https://pypi.tuna.tsinghua.edu.cn/simple"; then
  exit 0
fi

# 4) Direct wheel URL (user-provided) for truly offline environments.
if [[ -n "$CUSTOM_URL" ]]; then
  echo "Attempting direct download from ${CUSTOM_URL}..." >&2
  if command -v curl >/dev/null 2>&1; then
    curl -fL "$CUSTOM_URL" -o "${DEST}/Pillow-${VERSION}.whl" && exit 0
  elif command -v wget >/dev/null 2>&1; then
    wget -O "${DEST}/Pillow-${VERSION}.whl" "$CUSTOM_URL" && exit 0
  fi
fi

echo "Failed to download Pillow ${VERSION}. Provide a wheel via PILLOW_WHEEL_URL or copy it into ${DEST}/" >&2
exit 1
