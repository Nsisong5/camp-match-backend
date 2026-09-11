import asyncio
from fastapi.testclient import TestClient
from camp_match.app import create_app

def main():
    app = create_app()
    with TestClient(app) as client:
        # Get one ID
        print("--- GET /api/v1/universities (list) ---")
        list_resp = client.get("/api/v1/universities")
        print(f"List Status: {list_resp.status_code}")
        items = list_resp.json().get('items', [])
        print(f"List Count: {len(items)}")
        
        if items:
            uni_id = items[0]['id']
            print(f"\n--- GET /api/v1/universities/{uni_id} ---")
            resp = client.get(f"/api/v1/universities/{uni_id}")
            print(f"Individual Status: {resp.status_code}")
            print(f"Individual Body: {resp.json()}")

if __name__ == "__main__":
    main()
