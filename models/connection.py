import mysql.connector

import settings

rpg_db = mysql.connector.connect(
    host=settings.DB_HOST,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_DATABASE_NAME_DEV
)
