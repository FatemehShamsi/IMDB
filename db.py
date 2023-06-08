import requests
from bs4 import BeautifulSoup
from sqlalchemy import URL, create_engine, text

from sqlalchemy import ForeignKey
from sqlalchemy import String, INTEGER

from sqlalchemy.orm import Session, Mapped, DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy import exists
from sqlalchemy.orm import relationship
from sqlalchemy.orm import foreign
from sqlalchemy.orm import Session

from crawl import IMDB
from time import sleep

DB_NAME = 'Top_250_imdb'
PASSWORD = ''
USERNAME = ''

class Base(DeclarativeBase):
    pass


class Movie(Base):
    __tablename__ = 'movie'

    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    year: Mapped[int] = mapped_column(INTEGER())
    run_time: Mapped[int] = mapped_column(INTEGER())
    parental_guide: Mapped[str] = mapped_column(String(8))
    gross_us_canada: Mapped[int] = mapped_column(INTEGER(), nullable=True)

    cast = relationship("Cast", primaryjoin="Movie.id == foreign(Cast.movie_id)")
    crew = relationship("Crew", primaryjoin="Movie.id == foreign(Crew.movie_id)")
    genre = relationship("GenresMovie", primaryjoin="Movie.id == foreign(GenresMovie.movie_id)")


class Person(Base):
    __tablename__ = 'person'
    id: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(32))

    cast = relationship("Cast", primaryjoin="Person.id == foreign(Cast.movie_id)")
    crew = relationship("Crew", primaryjoin="Person.id == foreign(Crew.movie_id)")


class Cast(Base):
    __tablename__ = 'cast'

    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True)
    movie_id: Mapped[str] = mapped_column(String(8), ForeignKey("movie.id"))
    person_id: Mapped[str] = mapped_column(String(8), ForeignKey("person.id"))


class Crew(Base):
    __tablename__ = 'crew'
    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True)
    movie_id: Mapped[str] = mapped_column(String(8), ForeignKey("movie.id"))
    person_id: Mapped[str] = mapped_column(String(8), ForeignKey("person.id"))
    role: Mapped[str] = mapped_column(String(8))


class GenresMovie(Base):
    __tablename__ = 'genre'
    id: Mapped[int] = mapped_column(INTEGER(), primary_key=True)
    movie_id: Mapped[str] = mapped_column(String(8), ForeignKey("movie.id"))
    genre: Mapped[str] = mapped_column(String(16))


def create_database():
    url_object = URL.create('mysql+mysqlconnector',
                            username=USERNAME,
                            password=PASSWORD,
                            host='localhost')

    engine = create_engine(url_object)
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))
        conn.execute(text(f"CREATE DATABASE {DB_NAME}"))


def create_table():
    url_object = URL.create(
        "mysql+mysqlconnector",
        username=USERNAME,
        password=PASSWORD,
        host="localhost",
        database=DB_NAME
    )

    engine = create_engine(url_object)
    Base.metadata.create_all(engine)


def add_movie_data_to_database(data):
    url_object = URL.create(
        "mysql+mysqlconnector",
        username=USERNAME,
        password=PASSWORD,
        host="localhost",
        database=DB_NAME
    )

    engine = create_engine(url_object)
    session = Session(engine, autoflush=False)
    movie = Movie(
        id=data['movie_id'],
        title=data['title'],
        year=data['year'],
        run_time=data['runtime'],
        parental_guide=data['parental_guid'],
        gross_us_canada=data['gross_US_Canada'],
    )

    session.add(movie)
    session.commit()

    for gen in data['generes']:
        genre = GenresMovie(

            movie_id=data['movie_id'],
            genre=gen
        )
        session.add(genre)
        session.commit()

    direcs = data['directors']
    for idx in range(len(direcs['id'])):

        if session.query(exists().where(Person.id == direcs['id'][idx])).scalar():
            pass
        else:
            per = Person(
                id=direcs['id'][idx],
                name=direcs['name'][idx]
            )
            session.add(per)
            session.commit()

        di_cast = Crew(
            movie_id=data['movie_id'],
            person_id=direcs['id'][idx],
            role='director',

        )
        session.add(di_cast)
        session.commit()

    writ = data['writers']
    for idx in range(len(writ['id'])):
        if session.query(exists().where(Person.id == writ['id'][idx])).scalar():
            pass
        else:

            per = Person(
                id=writ['id'][idx],
                name=writ['name'][idx]
            )
            session.add(per)
            session.commit()

        di_cast = Crew(

            movie_id=data['movie_id'],
            person_id=writ['id'][idx],
            role='writer'

        )
        session.add(di_cast)
        session.commit()

    stars = data['stars']
    for idx in range(len(stars['id'])):
        if session.query(exists().where(Person.id == stars['id'][idx])).scalar():
            pass
        else:
            per = Person(
                id=stars['id'][idx],
                name=stars['name'][idx]
            )
            session.add(per)
            session.commit()
        di_cast = Cast(
            movie_id=data['movie_id'],
            person_id=stars['id'][idx]

        )
        session.add(di_cast)
        session.commit()



create_database()
create_table()
response = requests.get('https://www.imdb.com/chart/top/?ref_=nv_mv_250')
sop = BeautifulSoup(response.content, 'html.parser')
table_of_movies = sop.find(class_='lister-list').find_all('tr')

list_of_movies = []
for row_of_table in table_of_movies:
    movie_link = row_of_table.find('a')
    list_of_movies.append(movie_link.attrs['href'])

for idx, movie in enumerate(list_of_movies):

    site = IMDB(movie)
    data = site.movie_data()

    print(str(idx)+'. Loading ' + data['title'])
    print('--------------------------------------')

    add_movie_data_to_database(data)

    sleep(20)
    if (idx % 20) == 0:
        sleep(240)
