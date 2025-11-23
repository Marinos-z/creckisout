#!/usr/bin/env bash
set -euo pipefail

# Attempt to install Django using several strategies to work around restricted networks.
# Usage: ./scripts/install_django.sh [version]
# Defaults to version pinned in requirements.txt.

VERSION="${1:-5.2.8}"
PILLOW_VERSION="${PILLOW_VERSION:-11.1.0}"
REQ_LINE="django==${VERSION}"

# Helper to run pip with common options.
pip_install() {
  local index_url="$1"
  shift
  python -m pip install --no-cache-dir --index-url "$index_url" "$@"
}

django_installed=0
if python - <<'PY' 2>/dev/null; then
import django
print(f"Django already installed ({django.get_version()})")
PY
then
  django_installed=1
fi

if [[ $django_installed -eq 0 ]]; then
  # 1) Try the default PyPI index with the repo's certificate trust settings.
  echo "[1/5] Trying PyPI (https) for Django ${VERSION}..." >&2
  if pip_install "https://pypi.org/simple" "$REQ_LINE"; then
    django_installed=1
  else
    # 2) Try PyPI over HTTP to bypass potential TLS interception issues.
    echo "[2/5] Trying PyPI (http) for Django ${VERSION}..." >&2
    if pip_install "http://pypi.org/simple" "$REQ_LINE"; then
      django_installed=1
    else
      # 3) Try an alternate mirror that is often reachable in restricted environments.
      echo "[3/5] Trying Tsinghua mirror for Django ${VERSION}..." >&2
      if pip_install "https://pypi.tuna.tsinghua.edu.cn/simple" "$REQ_LINE"; then
        django_installed=1
      else
        # 4) Fallback: install from a locally provided wheel in the vendor directory.
        LOCAL_WHEEL=$(ls vendor/Django-*.whl 2>/dev/null | head -n1 || true)
        if [[ -n "$LOCAL_WHEEL" ]]; then
          echo "[4/5] Installing Django from local wheel: $LOCAL_WHEEL" >&2
          python -m pip install --no-cache-dir "$LOCAL_WHEEL"
          django_installed=1
        else
          # 5) Fallback: use OS packages (works only if apt repos are reachable).
          if command -v apt-get >/dev/null 2>&1; then
            echo "[5/5] Trying apt-get install python3-django..." >&2
            if apt-get update && apt-get install -y python3-django; then
              django_installed=1
            fi
          fi
        fi
      fi
    fi
  fi
fi

if [[ $django_installed -eq 0 ]]; then
  echo "Django installation failed. Place a wheel in vendor/ or adjust proxy settings." >&2
  exit 1
fi

# Pillow is required for ImageField. Try the same sequence but ignore failures in last resort.
if python - <<'PY' 2>/dev/null; then
from PIL import __version__
print(f"Pillow already installed ({__version__})")
PY
then
  exit 0
fi

echo "Attempting Pillow ${PILLOW_VERSION} installation..." >&2
if pip_install "https://pypi.org/simple" "pillow==${PILLOW_VERSION}"; then
  exit 0
fi

if pip_install "http://pypi.org/simple" "pillow==${PILLOW_VERSION}"; then
  exit 0
fi

if pip_install "https://pypi.tuna.tsinghua.edu.cn/simple" "pillow==${PILLOW_VERSION}"; then
  exit 0
fi

LOCAL_PILLOW=$(ls vendor/Pillow-*.whl 2>/dev/null | head -n1 || true)
if [[ -n "$LOCAL_PILLOW" ]]; then
  echo "Installing Pillow from local wheel: $LOCAL_PILLOW" >&2
  if python -m pip install --no-cache-dir "$LOCAL_PILLOW"; then
    exit 0
  fi
fi

if command -v apt-get >/dev/null 2>&1; then
  echo "Trying apt-get install python3-pil..." >&2
  if apt-get update && apt-get install -y python3-pil; then
    exit 0
  fi
fi

echo "Pillow installation failed. Place a wheel in vendor/ or adjust proxy settings." >&2
exit 1
