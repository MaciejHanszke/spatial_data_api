import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, declarative_base

db_user = os.getenv('DB_USER', "postgres")
db_password = os.getenv('DB_PASSWORD', '1234567890')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', "postgres")

if not all([db_user, db_password, db_host, db_name]):
    raise ValueError("Missing required database configuration in environment variables.")

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
SQL_ALCHEMY_DB = sa.create_engine(DATABASE_URL)
SQL_ALCHEMY_SESSION = sessionmaker(bind=SQL_ALCHEMY_DB)
SQL_ALCHEMY_BASE = declarative_base()
