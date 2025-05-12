#!/usr/bin/env bash
mkdir -p tmp
> tmp/missing.txt
for f in details/*.json; do
  jq -e '.description and .minPlayers and .imageUrl' "$f" >/dev/null ||
    echo "$f" >> tmp/missing.txt
done
echo "需補檔數量：$(wc -l < tmp/missing.txt)"
