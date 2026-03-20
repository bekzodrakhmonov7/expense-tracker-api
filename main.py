from api.api import router
from database.database import init_database

if __name__ == "__main__":
    import uvicorn
    init_database()
    uvicorn.run(router, host="0.0.0.0", port=8000)