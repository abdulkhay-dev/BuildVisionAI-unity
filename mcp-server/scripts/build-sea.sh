#!/usr/bin/env bash
# Builds house-mcp as a single executable (Node SEA): no Node.js needed on the user's machine.
# Output: build/house-mcp (for the platform/arch of the node running this script). macOS: ad-hoc signed.
set -euo pipefail
cd "$(dirname "$0")/.."

npm run build >/dev/null
mkdir -p build
npx esbuild dist/index.js --bundle --platform=node --format=cjs --target=node20 \
  --outfile=build/house-mcp.cjs --log-level=warning
cat > build/sea-config.json <<'JSON'
{ "main": "build/house-mcp.cjs", "output": "build/sea-prep.blob", "disableExperimentalSEAWarning": true, "useCodeCache": false }
JSON
node --experimental-sea-config build/sea-config.json

cp "$(command -v node)" build/house-mcp
chmod u+w build/house-mcp
if [[ "$(uname)" == "Darwin" ]]; then
  codesign --remove-signature build/house-mcp
  npx postject build/house-mcp NODE_SEA_BLOB build/sea-prep.blob \
    --sentinel-fuse NODE_SEA_FUSE_fce680ab2cc467b6e072b8b5df1996b2 --macho-segment-name NODE_SEA
  codesign --sign - build/house-mcp
else
  npx postject build/house-mcp NODE_SEA_BLOB build/sea-prep.blob \
    --sentinel-fuse NODE_SEA_FUSE_fce680ab2cc467b6e072b8b5df1996b2
fi
echo "built $(pwd)/build/house-mcp ($(du -h build/house-mcp | cut -f1), $(file -b build/house-mcp | cut -c1-40))"
