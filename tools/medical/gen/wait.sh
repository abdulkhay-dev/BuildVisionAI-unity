#!/bin/bash
# wait until Unity rendered every given id (its .txt newer than its design json), then print the results
cd "$(dirname "$0")/../../.."
for id in "$@"; do
  j=Assets/House4696/Resources/Medical/Designs/$id.json; t=tools/medical/renders/$id.txt
  n=0; until [ "$t" -nt "$j" ]; do sleep 2; n=$((n+1)); [ $n -gt 90 ] && { echo "$id: timeout"; break; }; done
  echo "$id: $(cat $t 2>/dev/null | head -5)"
done
