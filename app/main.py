import uvicorn

from config import CFG, ENV


if __name__ == "__main__":
    uvicorn.run(
        app="app:application",
        host="0.0.0.0",
        port=CFG.api.port,
        workers=CFG.api.workers,
        reload=True if ENV == "dev" else False,
    )
