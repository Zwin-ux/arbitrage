#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DIST_DIR="${ROOT}/dist-macos"
BUILD_DIR="${ROOT}/.tmp/macos-build"

python3 -m pip install -e ".[packaging]"
python3 -m PyInstaller \
  --noconfirm \
  --clean \
  --distpath "${DIST_DIR}" \
  --workpath "${BUILD_DIR}" \
  "${ROOT}/packaging/macos/market_data_recorder_app_macos.spec"

echo "macOS PoC build complete:"
echo "  ${DIST_DIR}"
echo
echo "Next steps:"
echo "  - verify .app launches"
echo "  - archive or zip the .app bundle"
echo "  - sign and notarize separately for public distribution"
