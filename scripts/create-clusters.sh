#!/usr/bin/env bash

echo "=== Creating 3 local clusters ==="

for CLOUD in aws gcp azure; do
  echo ""
  echo "→ Creating kind-$CLOUD..."
  kind create cluster --name "$CLOUD" --wait 60s
done

echo ""
echo "=== Clusters created ==="
kind get clusters
