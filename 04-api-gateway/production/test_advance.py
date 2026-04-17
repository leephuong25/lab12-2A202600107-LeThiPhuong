"""
Test suite cho production security stack.
Chạy: python test_advanced.py --test <test_name>
Tests: auth, rate-limit, cost-guard, all
"""
import sys
import json
import time
import argparse
import urllib.request
import urllib.error

BASE = "http://localhost:8000"


def get_token(username="student", password="demo123"):
    data = json.dumps({"username": username, "password": password}).encode()
    req = urllib.request.Request(
        f"{BASE}/auth/token",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


def ask(token, question="hello"):
    data = json.dumps({"question": question}).encode()
    req = urllib.request.Request(
        f"{BASE}/ask",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_auth():
    print("\n=== Test: Authentication ===")

    # Valid login
    try:
        token = get_token("student", "demo123")
        print(f"[PASS] Login OK, token: {token[:30]}...")
    except Exception as e:
        print(f"[FAIL] Login failed: {e}")
        return

    # Invalid login
    try:
        get_token("student", "wrongpass")
        print("[FAIL] Should have rejected bad password")
    except urllib.error.HTTPError as e:
        if e.code == 401:
            print("[PASS] Wrong password → 401")
        else:
            print(f"[FAIL] Expected 401, got {e.code}")

    # No token
    req = urllib.request.Request(
        f"{BASE}/ask",
        data=json.dumps({"question": "hi"}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        urllib.request.urlopen(req)
        print("[FAIL] Should have rejected missing token")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("[PASS] No token → 403")
        else:
            print(f"[FAIL] Expected 403, got {e.code}")


def test_rate_limit():
    print("\n=== Test: Rate Limiting ===")
    try:
        token = get_token("student", "demo123")
    except Exception as e:
        print(f"[FAIL] Could not get token: {e}")
        return

    results = {}
    print("Sending 21 requests rapidly...")
    for i in range(21):
        status, _ = ask(token, f"question {i}")
        results[status] = results.get(status, 0) + 1

    print(f"  200 OK: {results.get(200, 0)}")
    print(f"  429 Rate limited: {results.get(429, 0)}")

    if results.get(429, 0) > 0:
        print("[PASS] Rate limiter triggered")
    else:
        print("[INFO] No 429 yet (limit may be > 15 req/min)")


def test_cost_guard():
    print("\n=== Test: Cost Guard ===")
    try:
        token = get_token("teacher", "teach456")
    except Exception as e:
        print(f"[FAIL] Could not get token: {e}")
        return

    status, body = ask(token, "what is the budget status?")
    print(f"  Status: {status}")
    if status == 200:
        print(f"[PASS] Request succeeded: {body.get('answer', '')[:60]}")
    elif status == 503:
        print("[INFO] Daily budget exhausted → 503")
    else:
        print(f"[FAIL] Unexpected status {status}: {body}")


def test_all():
    test_auth()
    test_rate_limit()
    test_cost_guard()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", choices=["auth", "rate-limit", "cost-guard", "all"], default="all")
    args = parser.parse_args()

    tests = {
        "auth": test_auth,
        "rate-limit": test_rate_limit,
        "cost-guard": test_cost_guard,
        "all": test_all,
    }
    tests[args.test]()