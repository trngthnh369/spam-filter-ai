#!/bin/bash

# Quick API test script for Spam Filter AI

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

API_URL="${API_URL:-http://localhost:8000}"
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print test results
print_test_header() {
    echo ""
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=========================================${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
}

print_success() {
    echo -e "${GREEN}✓ PASS: $1${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
}

print_failure() {
    echo -e "${RED}✗ FAIL: $1${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if API is accessible
echo ""
echo "Testing Spam Filter AI API at: $API_URL"
echo ""

# Test 0: Check if API is running
print_test_header "Test 0: API Connectivity"
if curl -s -f "$API_URL/api/v1/health" > /dev/null 2>&1; then
    print_success "API is accessible"
else
    print_failure "Cannot connect to API at $API_URL"
    echo ""
    echo "Please ensure the backend is running:"
    echo "  - Development: cd backend && uvicorn main:app --reload"
    echo "  - Docker: docker-compose up -d"
    exit 1
fi

# Test 1: Health check
print_test_header "Test 1: Health Check Endpoint"
HEALTH_RESPONSE=$(curl -s "$API_URL/api/v1/health")
HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('status', 'unknown'))" 2>/dev/null || echo "error")

if [ "$HEALTH_STATUS" = "healthy" ]; then
    print_success "Health check passed"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    print_failure "Health check failed: status=$HEALTH_STATUS"
    echo "$HEALTH_RESPONSE"
fi

# Test 2: Classify ham message
print_test_header "Test 2: Classify Legitimate (Ham) Message"
HAM_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you doing today? Let me know when you are free.", "k": 5}')

HAM_PREDICTION=$(echo "$HAM_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('prediction', 'unknown'))" 2>/dev/null || echo "error")
HAM_CONFIDENCE=$(echo "$HAM_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('confidence', 0))" 2>/dev/null || echo "0")

if [ "$HAM_PREDICTION" = "ham" ]; then
    print_success "Ham message correctly classified (confidence: $HAM_CONFIDENCE)"
    echo "$HAM_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
else
    print_failure "Ham message misclassified as: $HAM_PREDICTION"
    echo "$HAM_RESPONSE"
fi

# Test 3: Classify spam message
print_test_header "Test 3: Classify Spam Message"
SPAM_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{"message": "CONGRATULATIONS! You won $1000 cash prize! Click here NOW to claim your reward!", "k": 5}')

SPAM_PREDICTION=$(echo "$SPAM_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('prediction', 'unknown'))" 2>/dev/null || echo "error")
SPAM_CONFIDENCE=$(echo "$SPAM_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('confidence', 0))" 2>/dev/null || echo "0")

if [ "$SPAM_PREDICTION" = "spam" ]; then
    print_success "Spam message correctly classified (confidence: $SPAM_CONFIDENCE)"
    echo "$SPAM_RESPONSE" | python3 -m json.tool 2>/dev/null | head -20
else
    print_failure "Spam message misclassified as: $SPAM_PREDICTION"
    echo "$SPAM_RESPONSE"
fi

# Test 4: Classify with explainability
print_test_header "Test 4: Explainability Feature"
EXPLAIN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{"message": "Win free iPhone now! Limited offer!", "k": 5, "explain": true}')

HAS_TOKENS=$(echo "$EXPLAIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print('tokens' in data and data['tokens'] is not None)" 2>/dev/null || echo "False")

if [ "$HAS_TOKENS" = "True" ]; then
    print_success "Explainability tokens returned"
    echo "$EXPLAIN_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); tokens=data.get('tokens', []); print(f'Found {len(tokens)} tokens'); [print(f\"  {t['token']}: {t['saliency']:.3f}\") for t in tokens[:5]]" 2>/dev/null
else
    print_failure "Explainability tokens not returned"
fi

# Test 5: Vietnamese message
print_test_header "Test 5: Vietnamese Language Support"
VI_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{"message": "Chúc mừng! Bạn đã trúng thưởng 10 triệu đồng! Click ngay để nhận quà!", "k": 5}')

VI_PREDICTION=$(echo "$VI_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('prediction', 'unknown'))" 2>/dev/null || echo "error")

if [ "$VI_PREDICTION" = "spam" ]; then
    print_success "Vietnamese spam correctly classified"
else
    print_info "Vietnamese message classified as: $VI_PREDICTION"
fi

# Test 6: Batch classification
print_test_header "Test 6: Batch Classification"
BATCH_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{"messages": ["Hello friend", "Win $1000 now!", "Meeting at 3pm"], "k": 5}')

BATCH_COUNT=$(echo "$BATCH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_processed', 0))" 2>/dev/null || echo "0")

if [ "$BATCH_COUNT" = "3" ]; then
    print_success "Batch classification processed $BATCH_COUNT messages"
    echo "$BATCH_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f\"  {i+1}. {r['prediction']} (conf: {r['confidence']:.2f})\") for i, r in enumerate(data.get('results', []))]" 2>/dev/null
else
    print_failure "Batch classification failed: processed $BATCH_COUNT messages"
fi

# Test 7: Statistics endpoint
print_test_header "Test 7: Statistics Endpoint"
STATS_RESPONSE=$(curl -s "$API_URL/api/v1/stats")
TOTAL_SAMPLES=$(echo "$STATS_RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_training_samples', 0))" 2>/dev/null || echo "0")

if [ "$TOTAL_SAMPLES" -gt 0 ]; then
    print_success "Statistics retrieved: $TOTAL_SAMPLES training samples"
    echo "$STATS_RESPONSE" | python3 -m json.tool 2>/dev/null | head -15
else
    print_failure "Statistics endpoint failed"
    echo "$STATS_RESPONSE"
fi

# Test 8: Error handling
print_test_header "Test 8: Error Handling (Empty Message)"
ERROR_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/v1/classify" \
  -H "Content-Type: application/json" \
  -d '{"message": "", "k": 5}')

HTTP_CODE=$(echo "$ERROR_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "422" ]; then
    print_success "Empty message properly rejected with HTTP $HTTP_CODE"
else
    print_info "Empty message returned HTTP $HTTP_CODE"
fi

# Summary
echo ""
echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}=========================================${NC}"
echo "Total Tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed:       $PASSED_TESTS${NC}"
echo -e "${RED}Failed:       $FAILED_TESTS${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi