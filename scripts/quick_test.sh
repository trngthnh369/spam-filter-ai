#!/bin/bash

# Quick API test script

API_URL="http://localhost:8000"

echo "Testing Spam Filter AI API..."
echo ""

# Test 1: Health check
echo "[1] Health check..."
curl -s "$API_URL/api/v1/health" | jq '.'
echo ""

# Test 2: Classify ham
echo "[2] Testing ham message..."
curl -s -X POST "$API_URL/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "k": 5}' | jq '.'
echo ""

# Test 3: Classify spam
echo "[3] Testing spam message..."
curl -s -X POST "$API_URL/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{"message": "Win $1000 now! Click here!", "k": 5}' | jq '.'
echo ""

# Test 4: Get stats
echo "[4] Getting statistics..."
curl -s "$API_URL/api/v1/stats" | jq '.'
echo ""

echo "✓ API tests complete"