#!/usr/bin/env bash
# Builds Stems-<version>.dmg with the pixel-art background and drag arrow.
# Run on a Mac (needs hdiutil + tiffutil) with create-dmg: brew install create-dmg
#
#   dmg/make-dmg.sh /path/to/Stems.app 1.0 [output-dir]
#
# Set SIGN_IDENTITY="Developer ID Application: ..." to codesign the DMG.
# Notarising and stapling stay in your existing release flow.
set -euo pipefail

APP="${1:?usage: make-dmg.sh /path/to/Stems.app version [output-dir]}"
VERSION="${2:?usage: make-dmg.sh /path/to/Stems.app version [output-dir]}"
OUT_DIR="${3:-.}"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="$OUT_DIR/Stems-$VERSION.dmg"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

# Retina-aware background: one TIFF holding the 1x and 2x images.
tiffutil -cathidpicheck "$HERE/background.png" "$HERE/background@2x.png" \
  -out "$WORK/background.tiff"

mkdir "$WORK/stage"
cp -R "$APP" "$WORK/stage/Stems.app"
rm -f "$OUT"

# The art is 660x400 (the image runs on past it); the window is 100pt taller for the title bar, tab bar
# and path bar, which Finder counts in the window size. Icon centres are at x=165 and
# x=495 (the art puts the arrow between them) and y=188.
create-dmg \
  --volname "Stems" \
  --background "$WORK/background.tiff" \
  --window-pos 200 120 \
  --window-size 660 500 \
  --icon-size 128 \
  --text-size 13 \
  --icon "Stems.app" 165 188 \
  --hide-extension "Stems.app" \
  --app-drop-link 495 188 \
  --no-internet-enable \
  ${SIGN_IDENTITY:+--codesign "$SIGN_IDENTITY"} \
  "$OUT" "$WORK/stage"

echo "Built $OUT"
