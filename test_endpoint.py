import asyncio
from fastapi.testclient import TestClient
from camp_match.app import create_app

def main():
    app = create_app()
    with TestClient(app) as client:
        print("--- GET /api/v1/universities ---")
        response = client.get("/api/v1/universities")
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")

if __name__ == "__main__":
    main()
