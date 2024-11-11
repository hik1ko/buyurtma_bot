from dotenv import load_dotenv
from sqlalchemy import create_engine
from os import getenv

load_dotenv()

class Db:
    DB_USER = getenv('DB_USER')
    DB_PORT = getenv('DB_PORT')
    DB_HOST = getenv('DB_HOST')
    DB_PASSWORD = getenv('DB_PASSWORD')
    DB_NAME = getenv('DB_NAME')
    URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(Db.URL)
