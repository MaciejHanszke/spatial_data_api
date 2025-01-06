import logging
import time

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from sqlalchemy_setup import SQL_ALCHEMY_BASE, SQL_ALCHEMY_DB
from generic.routes import generic_router
from project.routes import project_router

logger = logging.getLogger('uvicorn.error')

MAX_RECONNECT_RETRIES = 4

def main():
    for retry in range(MAX_RECONNECT_RETRIES):
        try:
            logger.info(f"Attempting database connection {retry+1}/{MAX_RECONNECT_RETRIES}")
            SQL_ALCHEMY_BASE.metadata.create_all(SQL_ALCHEMY_DB)
            break
        except OperationalError as e:
            logger.warning(e)
            if (retry + 1) == MAX_RECONNECT_RETRIES:
                raise OperationalError("Max retries for connecting database reached. Exiting.", None, e)
            exponential_backoff_time = (retry + 1) * 5
            logger.warning(f"Failed DB connection. Retrying after {exponential_backoff_time} seconds")
            time.sleep(exponential_backoff_time)
    logger.info("DB Connection established.")

    return FastAPI(
        title="Spatial Data API",
        description="Basic CRUD application allowing to interact with so called \"Projects\".",
        version="0.0.1"
    )

# TODO ALEMBIC?
# TODO MOVE THE DATABASE INIT SOMEWHERE ELSE
# TODO MAKE THE HEALTHCHECK CHECK THE DB CONNECTION

app = main()
app.include_router(generic_router)
app.include_router(project_router, prefix="/project")

