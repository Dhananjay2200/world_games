"""
API Verification Script for WorldGames AI endpoints using FastAPI TestClient.
"""

from fastapi.testclient import TestClient
from app.main import app


def test_api_endpoints():
    print("=" * 65)
    print(" WorldGames AI - FastAPI Endpoints Diagnostic")
    print("=" * 65)
    
    with TestClient(app) as client:
        # 1. Health check
        print("[*] Testing GET /api/v1/health...")
        res = client.get("/api/v1/health")
        print(f"    Status: {res.status_code} | Payload: {res.json()}")
        assert res.status_code == 200
        
        # 2. Public Feed
        print("[*] Testing GET /api/v1/publish/feed...")
        res = client.get("/api/v1/publish/feed")
        data = res.json()
        print(f"    Status: {res.status_code} | Total Published: {data.get('total')}")
        if data.get("articles"):
            art = data["articles"][0]
            print(f"    Sample Article: '{art.get('title')}'")
            print(f"    Category: {art.get('category')} | Region: {art.get('origin_region')} | Score: {art.get('score')}")
        assert res.status_code == 200
        
        # 3. System Stats
        print("[*] Testing GET /api/v1/publish/stats...")
        res = client.get("/api/v1/publish/stats")
        print(f"    Status: {res.status_code} | Stats: {res.json()}")
        assert res.status_code == 200

        # 4. Filter by Category
        print("[*] Testing GET /api/v1/publish/feed with combinatorial filter (category='Indigenous, Folk & Traditional Games')...")
        res = client.get("/api/v1/publish/feed?category=Indigenous,%20Folk%20%26%20Traditional%20Games")
        print(f"    Status: {res.status_code} | Matches: {res.json().get('total')}")
        assert res.status_code == 200

        # 5. Taxonomy endpoint
        print("[*] Testing GET /api/v1/topics/taxonomy...")
        res = client.get("/api/v1/topics/taxonomy")
        tax = res.json()
        print(f"    Regions ({len(tax.get('regions', []))}): {tax.get('regions')[:3]}...")
        print(f"    Categories ({len(tax.get('categories', []))}): {tax.get('categories')[:3]}...")
        assert res.status_code == 200

        # 6. Auth login endpoint
        print("[*] Testing POST /api/v1/auth/login...")
        login_res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
        print(f"    Status: {login_res.status_code} | Token type: {login_res.json().get('token_type')}")
        assert login_res.status_code == 200

    print("[+] All API endpoints verified and operational!")
    print("=" * 65)


if __name__ == "__main__":
    test_api_endpoints()
