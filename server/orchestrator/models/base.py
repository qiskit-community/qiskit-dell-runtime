from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.ext.declarative import declarative_base


db_host = os.environ['DB_HOST']
db_port = os.environ['DB_PORT']
db_user = os.environ['DB_USER']
db_password = os.environ['DB_PASSWORD']
db_name = os.environ['DB_NAME']

db_string = f"mysql+mysqldb://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
engine = create_engine(db_string)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
