#!/usr/bin/env bash
# Packages Builds/App/Windows (House.exe + data) into Builds/App/House-<version>-win64.zip, on a Mac:
#   1) builds the MCP server as a Windows single executable: the same bundle as on macOS (mcp-server/scripts/build-sea.sh)
#      injected into the official node.exe for win-x64 of the local Node version (downloaded once into .cache/node-win,
#      checked against nodejs.org's SHASUMS256) → Builds/App/Windows/mcp/house-mcp.exe, where the app looks for it
#   2) zips the folder
# Build the app first: Unity menu House 46-96 → App → Build Windows app (x64), or batch mode:
#   Unity -batchmode -quit -projectPath . -buildTarget Win64 -executeMethod House4696.Build.AppBuild.BuildWindowsCli
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="$ROOT/Builds/App/Windows"
[[ -f "$APP/House.exe" ]] || { echo "no $APP/House.exe — build the Windows app in Unity first"; exit 1; }
VERSION="$(sed -n 's/.*public const string Version = "\(.*\)";.*/\1/p' "$ROOT/Assets/House4696/Runtime/App/HouseBootstrap.cs")"
ZIP="$ROOT/Builds/App/House-$VERSION-win64.zip"

# a Node >= 20 with single-executable support (nvm's default may be older)
if ! node -e 'process.exit(+process.versions.node.split(".")[0] >= 20 ? 0 : 1)' 2>/dev/null; then
  export PATH="$(ls -d "$HOME"/.nvm/versions/node/v2[0-9]*/bin 2>/dev/null | tail -1):$PATH"
fi
NODE_VERSION="$(node --version)"
CACHE="$ROOT/.cache/node-win/$NODE_VERSION"
if [[ ! -f "$CACHE/node.exe" ]]; then
  mkdir -p "$CACHE"
  curl -sSfL -o "$CACHE/node.exe" "https://nodejs.org/dist/$NODE_VERSION/win-x64/node.exe"
  curl -sSfL -o "$CACHE/SHASUMS256.txt" "https://nodejs.org/dist/$NODE_VERSION/SHASUMS256.txt"
fi
want="$(grep ' win-x64/node.exe$' "$CACHE/SHASUMS256.txt" | cut -d' ' -f1)"
have="$(shasum -a 256 "$CACHE/node.exe" | cut -d' ' -f1)"
[[ "$want" == "$have" ]] || { echo "node.exe checksum mismatch — delete $CACHE and retry"; exit 1; }

"$ROOT/mcp-server/scripts/build-sea.sh" >/dev/null      # the bundle and its SEA blob (made by this Node version)
cd "$ROOT/mcp-server"
cp "$CACHE/node.exe" build/house-mcp.exe
chmod u+w build/house-mcp.exe
# the injection breaks node.exe's Authenticode signature (Windows may show SmartScreen on first run)
npx postject build/house-mcp.exe NODE_SEA_BLOB build/sea-prep.blob \
  --sentinel-fuse NODE_SEA_FUSE_fce680ab2cc467b6e072b8b5df1996b2 >/dev/null 2>&1

mkdir -p "$APP/mcp"
cp build/house-mcp.exe "$APP/mcp/house-mcp.exe"
cp README.md "$APP/mcp/README.md"
echo "mcp: $APP/mcp/house-mcp.exe ($(du -h "$APP/mcp/house-mcp.exe" | cut -f1))"

# the archive unpacks into a "House-<version>" folder
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
cp -R "$APP" "$STAGE/House-$VERSION"
rm -rf "$STAGE/House-$VERSION"/*_BackUpThisFolder_ButDontShipItWithYourGame
rm -f "$ZIP"
ditto -c -k --norsrc --noextattr --noqtn --keepParent "$STAGE/House-$VERSION" "$ZIP"
echo "zip: $ZIP ($(du -h "$ZIP" | cut -f1))"
