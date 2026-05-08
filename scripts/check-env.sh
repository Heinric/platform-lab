#!/usr/bin/env bash

echo "=== Platform Lab — Local Environment Check ==="

PASS=0
FAIL=0

check_cmd() {
  local name=$1
  if command -v "$name" &>/dev/null; then
    echo "✓ $name"
    PASS=$((PASS+1))
  else
    echo "✗ $name — NOT FOUND"
    FAIL=$((FAIL+1))
  fi
}

check_cmd docker
check_cmd kind
check_cmd kubectl
check_cmd terraform
check_cmd helm
check_cmd aws
check_cmd localstack

echo ""
docker info &>/dev/null && echo "✓ Docker daemon running" || echo "✗ Docker daemon NOT running"
echo ""
echo "Result: $PASS ok, $FAIL missing"
