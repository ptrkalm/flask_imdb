from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from models import Base, Movie

SQLALCHEMY_DATABSE_URL = 'sqlite:///database.db'

engine = create_engine(
    SQLALCHEMY_DATABSE_URL,
    connect_args={
         'check_same_thread': False
    })

Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
