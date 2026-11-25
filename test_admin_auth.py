"""
Test script for Admin Authentication and Session Lifecycle.
Verifies login, token signing, whitespace trimming, and unauthorized access rejection.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings


def test_auth_lifecycle():
    settings = get_settings()
    print("=" * 65)
    print(" WorldGames AI - Admin Authentication Diagnostic")
    print("=" * 65)
    
    with TestClient(app) as client:
        # 1. Correct credentials
        print(f"[*] Testing valid login ({settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD})...")
        res = client.post("/api/v1/auth/login", json={
            "username": settings.ADMIN_USERNAME,
            "password": settings.ADMIN_PASSWORD,
        })
        print(f"    Status: {res.status_code}")
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data and "token" in data
        token = data["access_token"]
        print(f"    [+] Login succeeded. Token received: {token[:25]}...")

        # 2. Whitespace trimming test
        print("[*] Testing login with accidental whitespace ('  admin  ')...")
        res_ws = client.post("/api/v1/auth/login", json={
            "username": f"  {settings.ADMIN_USERNAME}  ",
            "password": f"  {settings.ADMIN_PASSWORD}  ",
        })
        print(f"    Status: {res_ws.status_code}")
        assert res_ws.status_code == 200
        print("    [+] Whitespace trimming verified.")

        # 3. Invalid password test
        print("[*] Testing invalid credentials rejection...")
        res_bad = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrong_password_999",
        })
        print(f"    Status: {res_bad.status_code} | Error: {res_bad.json().get('detail')}")
        assert res_bad.status_code == 401
        print("    [+] Unauthorized rejection verified.")

        # 4. Token verification endpoint
        print("[*] Testing token verification endpoint (/api/v1/auth/verify)...")
        res_verify = client.get("/api/v1/auth/verify", headers={"Authorization": f"Bearer {token}"})
        print(f"    Status: {res_verify.status_code} | Payload: {res_verify.json()}")
        assert res_verify.status_code == 200
        print("    [+] Token successfully authenticated and validated.")

    print("\n[+] All Admin Authentication tests passed successfully!")
    print("=" * 65)


if __name__ == "__main__":
    test_auth_lifecycle()
