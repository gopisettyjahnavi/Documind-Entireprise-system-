"""
Demo Script for DocuMind Enterprise

This script demonstrates the RAG system with various test queries.
"""

import requests
import json
import time
from typing import List, Dict

# API Configuration
API_BASE_URL = "http://localhost:8000"


def test_health() -> bool:
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            return True
        else:
            print(f"❌ API Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False


def query_api(question: str) -> Dict:
    """Send a query to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/query",
            json={"question": question},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}


def run_demo():
    """Run the complete demo"""
    print("=" * 80)
    print("DocuMind Enterprise - Demo Script")
    print("=" * 80)
    print()
    
    # Test 1: Health Check
    print("Test 1: Health Check")
    print("-" * 80)
    if not test_health():
        print("\n⚠️  API is not running. Please start it with:")
        print("   python -m uvicorn backend.app:app --reload")
        return
    print()
    
    # Test 2: In-Scope Questions
    print("Test 2: In-Scope Questions (Should Answer)")
    print("-" * 80)
    
    in_scope_questions = [
        "What are the main policies covered in the documents?",
        "What are the eligibility criteria for scholarships?",
        "What is the penalty for providing false information?",
    ]
    
    for i, question in enumerate(in_scope_questions, 1):
        print(f"\n📝 Question {i}: {question}")
        result = query_api(question)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Answer: {result['answer'][:200]}...")
        time.sleep(1)  # Rate limiting
    
    print()
    
    # Test 3: Out-of-Scope Questions
    print("Test 3: Out-of-Scope Questions (Should Refuse)")
    print("-" * 80)
    
    out_of_scope_questions = [
        "What is the weather today?",
        "Who is the president of the United States?",
        "What is 2+2?",
    ]
    
    for i, question in enumerate(out_of_scope_questions, 1):
        print(f"\n📝 Question {i}: {question}")
        result = query_api(question)
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            answer = result['answer']
            if "don't know" in answer.lower() or "not available" in answer.lower():
                print(f"✅ Correctly Refused: {answer}")
            else:
                print(f"⚠️  Unexpected Answer: {answer}")
        time.sleep(1)
    
    print()
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print("\n💡 Tips:")
    print("  - Visit http://localhost:8000/docs for interactive API testing")
    print("  - Check http://localhost:8000/health for system status")
    print("  - Modify questions in this script to test custom queries")


if __name__ == "__main__":
    run_demo()
