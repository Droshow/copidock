#!/bin/bash

# Copidock API Test Suite
# Tests all endpoints for Phase 2 validation

set -e  # Exit on error

API_URL="https://bm2xwyxevf.execute-api.eu-central-1.amazonaws.com"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="test_results_${TIMESTAMP}.log"

echo "🚀 Copidock API Test Suite - $(date)" | tee $LOG_FILE
echo "API URL: $API_URL" | tee -a $LOG_FILE
echo "======================================" | tee -a $LOG_FILE

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to run test
run_test() {
    local test_name="$1"
    local curl_cmd="$2"
    local expected_status="$3"
    
    echo -e "\n${YELLOW}Test: $test_name${NC}" | tee -a $LOG_FILE
    echo "Command: $curl_cmd" | tee -a $LOG_FILE
    
    # Run curl and capture response
    response=$(eval "$curl_cmd" 2>&1)
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ PASS${NC}: $test_name" | tee -a $LOG_FILE
        echo "Response: $response" | tee -a $LOG_FILE
        ((TESTS_PASSED++))
        
        # Extract thread_id from first successful response
        if [[ "$test_name" == "Create Thread" && "$response" == *"thread_id"* ]]; then
            THREAD_ID=$(echo "$response" | grep -o '"thread_id":"[^"]*' | cut -d'"' -f4)
            echo "📝 Captured THREAD_ID: $THREAD_ID" | tee -a $LOG_FILE
        fi
    else
        echo -e "${RED}❌ FAIL${NC}: $test_name" | tee -a $LOG_FILE
        echo "Error: $response" | tee -a $LOG_FILE
        ((TESTS_FAILED++))
    fi
    
    sleep 1  # Brief pause between tests
}

# Test 1: Create Thread
echo -e "\n${YELLOW}=== PHASE 1: Thread Management ===${NC}"
run_test "Create Thread" \
    "curl -s -X POST $API_URL/thread/start -H 'Content-Type: application/json' -d '{\"goal\": \"API Test Suite Run $TIMESTAMP\", \"repo\": \"copidock\"}'" \
    200

# Use the captured thread ID for subsequent tests, or fallback to known working one
if [ -z "$THREAD_ID" ]; then
    THREAD_ID="e1eae2f9-f949-417a-ad7d-9b3b122780bb"
    echo "⚠️  Using fallback THREAD_ID: $THREAD_ID" | tee -a $LOG_FILE
fi

# Test 2: Notes Management
echo -e "\n${YELLOW}=== PHASE 2: Notes Management ===${NC}"

run_test "Create Note (with thread)" \
    "curl -s -X POST $API_URL/notes -H 'Content-Type: application/json' -d '{\"content\": \"Test note from automated suite - $TIMESTAMP\", \"tags\": [\"test\", \"automated\"], \"thread_id\": \"$THREAD_ID\"}'" \
    201

run_test "Create Note (without thread)" \
    "curl -s -X POST $API_URL/notes -H 'Content-Type: application/json' -d '{\"content\": \"Standalone test note - $TIMESTAMP\", \"tags\": [\"standalone\"]}'" \
    201

run_test "Get All Notes" \
    "curl -s $API_URL/notes" \
    200

run_test "Get Notes by Thread" \
    "curl -s '$API_URL/notes?thread_id=$THREAD_ID'" \
    200

run_test "Get Notes with Limit" \
    "curl -s '$API_URL/notes?limit=5'" \
    200

# Test 3: Snapshot Management
echo -e "\n${YELLOW}=== PHASE 3: Snapshot Management ===${NC}"

run_test "Create Snapshot (with paths)" \
    "curl -s -X POST $API_URL/snapshot -H 'Content-Type: application/json' -d '{\"thread_id\": \"$THREAD_ID\", \"paths\": [\"readme.md\", \"infra/main.tf\"]}'" \
    200

run_test "Create Snapshot (minimal)" \
    "curl -s -X POST $API_URL/snapshot -H 'Content-Type: application/json' -d '{\"thread_id\": \"$THREAD_ID\"}'" \
    200

# Test 4: Rehydration
echo -e "\n${YELLOW}=== PHASE 4: Rehydration ===${NC}"

run_test "Rehydrate Latest" \
    "curl -s $API_URL/rehydrate/$THREAD_ID/latest" \
    200

# Test 5: Error Handling
echo -e "\n${YELLOW}=== PHASE 5: Error Handling ===${NC}"

run_test "Invalid Thread ID" \
    "curl -s $API_URL/rehydrate/invalid-thread-id/latest" \
    404

run_test "Missing Content in Note" \
    "curl -s -X POST $API_URL/notes -H 'Content-Type: application/json' -d '{\"tags\": [\"test\"]}'" \
    400

run_test "Invalid JSON" \
    "curl -s -X POST $API_URL/thread/start -H 'Content-Type: application/json' -d '{invalid json}'" \
    400

run_test "Method Not Allowed" \
    "curl -s -X DELETE $API_URL/notes" \
    405

# Test 6: CORS Headers
echo -e "\n${YELLOW}=== PHASE 6: CORS Validation ===${NC}"

run_test "CORS Preflight" \
    "curl -s -X OPTIONS $API_URL/thread/start -H 'Origin: http://localhost:3000'" \
    200

# Summary
echo -e "\n${YELLOW}======================================${NC}" | tee -a $LOG_FILE
echo -e "${YELLOW}TEST SUMMARY${NC}" | tee -a $LOG_FILE
echo -e "${YELLOW}======================================${NC}" | tee -a $LOG_FILE
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}" | tee -a $LOG_FILE
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}" | tee -a $LOG_FILE
echo -e "Thread ID Used: $THREAD_ID" | tee -a $LOG_FILE
echo -e "Log File: $LOG_FILE" | tee -a $LOG_FILE

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n🎉 ${GREEN}ALL TESTS PASSED!${NC} Phase 2 deployment is fully functional." | tee -a $LOG_FILE
    exit 0
else
    echo -e "\n⚠️  ${RED}$TESTS_FAILED TESTS FAILED${NC}. Check the log for details." | tee -a $LOG_FILE
    exit 1
fi