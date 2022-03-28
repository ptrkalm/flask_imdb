from sqlalchemy import *
from sqlalchemy.orm import declarative_base
Base = declarative_base()


class Movie(Base):
    __tablename__ = 'collection'

    imdbId = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    genre = Column(String, nullable=False)
    imdbRating = Column(Float, nullable=False)
    poster = Column(String)
    myRating = Column(Integer)

    def as_dict(self):
        return {
            column.name: str(getattr(self, column.name))
            for column in self.__table__.columns
        }
