import uvicorn

from config import CFG_SERVICE, ENV


if __name__ == "__main__":
    uvicorn.run(
        app="app:application",
        host="0.0.0.0",
        port=CFG_SERVICE.api.port,
        workers=CFG_SERVICE.api.workers,
        reload=True if ENV == "dev" else False,
    )
