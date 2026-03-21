from api.api import router
from database.database import init_database, seed_categories

if __name__ == "__main__":
    import uvicorn

    init_database()
    seed_categories()
    uvicorn.run(router, host="0.0.0.0", port=8000)

