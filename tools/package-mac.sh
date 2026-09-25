#!/usr/bin/env bash
# Packages Builds/App/macOS/House.app into Builds/App/House-<version>.dmg:
#   1) builds the MCP server as a single executable (no Node needed) and puts it into the app:
#      House.app/Contents/Resources/mcp/house-mcp
#   2) ad-hoc signs the bundle (inserted files invalidate Unity's signature)
#   3) creates a compressed dmg with an Applications shortcut
# Build the app first: Unity menu House 46-96 → App → Build macOS app.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/Builds/App/macOS/House.app"
VERSION="$(/usr/libexec/PlistBuddy -c 'Print CFBundleShortVersionString' "$APP/Contents/Info.plist")"
DMG="$ROOT/Builds/App/House-$VERSION.dmg"
[[ -d "$APP" ]] || { echo "no $APP — build the app in Unity first"; exit 1; }

# a Node >= 20 with single-executable support (nvm's default may be older)
if ! node -e 'process.exit(+process.versions.node.split(".")[0] >= 20 ? 0 : 1)' 2>/dev/null; then
  export PATH="$(ls -d "$HOME"/.nvm/versions/node/v2[0-9]*/bin 2>/dev/null | tail -1):$PATH"
fi
"$ROOT/mcp-server/scripts/build-sea.sh"

mkdir -p "$APP/Contents/Resources/mcp"
cp "$ROOT/mcp-server/build/house-mcp" "$APP/Contents/Resources/mcp/house-mcp"
cp "$ROOT/mcp-server/README.md" "$APP/Contents/Resources/mcp/README.md"
codesign --force --deep --sign - "$APP"
codesign --verify --deep "$APP" && echo "signed (ad-hoc): $APP"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"
rm -f "$DMG"
hdiutil create -volname "House $VERSION" -srcfolder "$STAGE" -ov -format UDZO "$DMG" >/dev/null
echo "dmg: $DMG ($(du -h "$DMG" | cut -f1))"
