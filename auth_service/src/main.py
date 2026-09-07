import logging

import uvicorn
from fastapi import FastAPI
from src.api.routes.router import router
from src.logging_config import configure_logging

logger = logging.getLogger(__name__)



def create_app() -> FastAPI:
    app = FastAPI(
        title="Auth Service",
    )

    app.include_router(router)

    return app


app = create_app()


def main() -> None:
    configure_logging()
    logger.info("Starting auth_service...")

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None,
    )


if __name__ == "__main__":
    main()
