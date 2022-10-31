import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_DATABASE_NAME_DEV = os.getenv('DB_DATABASE_NAME_DEV')
DB_DATABASE_NAME_PRD = os.getenv('DB_DATABASE_NAME_PRD')