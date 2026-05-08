#!/usr/bin/env bash

CLOUD=${1:-""}

if [[ -z "$CLOUD" ]]; then
  echo "Usage: ./scripts/use-cloud.sh [aws|gcp|azure]"
  kubectl config get-contexts
  exit 0
fi

kubectl config use-context "kind-$CLOUD"
echo "→ Now on: kind-$CLOUD"
