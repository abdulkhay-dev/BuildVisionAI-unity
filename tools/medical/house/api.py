"""api.py <command> [args.json file]: calls the running House app's local API (~/.house-app/api.json)."""
import json, os, sys, urllib.request
cfg = json.load(open(os.path.expanduser("~/.house-app/api.json")))
args = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
req = urllib.request.Request(cfg["url"], json.dumps({"command": sys.argv[1], "args": args}).encode(),
                             {"Authorization": "Bearer " + cfg["token"], "Content-Type": "application/json"})
print(urllib.request.urlopen(req, timeout=600).read().decode())
