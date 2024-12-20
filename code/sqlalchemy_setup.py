import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base

db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')

if not all([db_user, db_password, db_host, db_name]):
    raise ValueError("Missing required database configuration in environment variables.")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
SQL_ALCHEMY_DB = sa.create_engine(DATABASE_URL)
SQL_ALCHEMY_SESSION = sessionmaker(bind=SQL_ALCHEMY_DB)
SQL_ALCHEMY_BASE = declarative_base()
