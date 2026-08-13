import uvicorn

from camp_match.app import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("camp_match.main:app", host="0.0.0.0", port=8000, reload=True)
